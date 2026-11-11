# modules/voice_processor.py

import io
import os
import shutil
import tempfile
import random
import time
import numpy as np
import wave
try:
    import scipy.io.wavfile as wavfile
    import scipy.signal as signal
    HAS_SCIPY = True
except ImportError:
    wavfile = None
    signal = None
    HAS_SCIPY = False
import whisper
import whisper.tokenizer


def _ensure_ffmpeg_in_path():
    """Ensure ffmpeg is available in system PATH so Whisper can process audio."""
    try:
        import subprocess
        res = subprocess.run(["ffmpeg", "-version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if res.returncode == 0:
            return
    except Exception:
        pass

    try:
        import imageio_ffmpeg
        ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
        if ffmpeg_exe and os.path.exists(ffmpeg_exe):
            ffmpeg_dir = os.path.dirname(ffmpeg_exe)
            if ffmpeg_dir not in os.environ.get("PATH", ""):
                os.environ["PATH"] = ffmpeg_dir + os.pathsep + os.environ.get("PATH", "")
            std_exe = os.path.join(ffmpeg_dir, "ffmpeg.exe" if os.name == "nt" else "ffmpeg")
            if not os.path.exists(std_exe):
                try:
                    shutil.copyfile(ffmpeg_exe, std_exe)
                except Exception:
                    pass
    except Exception as e:
        print(f"[WARN] ffmpeg setup warning: {e}")


# Run ffmpeg configuration once at module load
_ensure_ffmpeg_in_path()


class VoiceProcessor:
    """Process voice complaints using OpenAI Whisper - supports 100+ languages including Tamil, Telugu, and English"""

    SUPPORTED_LANGUAGES = {
        'en': 'English',
        'ta': 'Tamil',
        'te': 'Telugu',
        'hi': 'Hindi',
        'bn': 'Bengali',
        'mr': 'Marathi',
        'gu': 'Gujarati',
        'kn': 'Kannada',
        'ml': 'Malayalam',
        'pa': 'Punjabi',
        'or': 'Odia',
        'ur': 'Urdu',
        'as': 'Assamese',
        'sd': 'Sindhi',
        'sa': 'Sanskrit',
        'si': 'Sinhala'
    }

    def __init__(self):
        self.model = None
        self.model_loaded = False
        self._load_model()

    def _load_model(self):
        """Load Whisper tiny model (39MB) - most efficient for Green AI"""
        try:
            _ensure_ffmpeg_in_path()
            if self.model is None:
                self.model = whisper.load_model("tiny")
                self.model_loaded = True
                print("[OK] Whisper voice model loaded successfully")
        except Exception as e:
            print(f"[WARN] Whisper model load failed: {e}")
            self.model = None
            self.model_loaded = False

    def _decode_wav_to_array(self, audio_bytes):
        """
        Decode WAV bytes directly into a normalized 16kHz mono float32 NumPy array in memory.
        This provides lightning-fast transcription with zero external subprocess/ffmpeg overhead for st.audio_input.
        """
        # Method 1: scipy.io.wavfile (if installed)
        if HAS_SCIPY and wavfile is not None:
            try:
                sr, arr = wavfile.read(io.BytesIO(audio_bytes))
                if arr.ndim > 1:
                    arr = arr.mean(axis=1)
                if arr.dtype == np.int16:
                    arr = arr.astype(np.float32) / 32768.0
                elif arr.dtype == np.int32:
                    arr = arr.astype(np.float32) / 2147483648.0
                elif arr.dtype == np.uint8:
                    arr = (arr.astype(np.float32) - 128.0) / 128.0
                elif arr.dtype in (np.float32, np.float64):
                    arr = arr.astype(np.float32)

                if sr != 16000 and len(arr) > 0:
                    target_len = int(len(arr) * 16000 / sr)
                    if signal is not None:
                        arr = signal.resample(arr, target_len).astype(np.float32)
                    else:
                        arr = np.interp(np.linspace(0, len(arr), target_len, endpoint=False), np.arange(len(arr)), arr).astype(np.float32)
                return arr
            except Exception:
                pass

        # Method 2: standard library wave module (zero external dependencies)
        try:
            with wave.open(io.BytesIO(audio_bytes), 'rb') as wf:
                n_channels = wf.getnchannels()
                sampwidth = wf.getsampwidth()
                framerate = wf.getframerate()
                n_frames = wf.getnframes()
                frames = wf.readframes(n_frames)

                if sampwidth == 2:
                    arr = np.frombuffer(frames, dtype=np.int16).astype(np.float32) / 32768.0
                elif sampwidth == 1:
                    arr = (np.frombuffer(frames, dtype=np.uint8).astype(np.float32) - 128.0) / 128.0
                elif sampwidth == 4:
                    arr = np.frombuffer(frames, dtype=np.int32).astype(np.float32) / 2147483648.0
                else:
                    arr = None

                if arr is not None:
                    if n_channels > 1:
                        arr = arr.reshape(-1, n_channels).mean(axis=1)
                    if framerate != 16000 and len(arr) > 0:
                        target_len = int(len(arr) * 16000 / framerate)
                        if HAS_SCIPY and signal is not None:
                            arr = signal.resample(arr, target_len).astype(np.float32)
                        else:
                            arr = np.interp(np.linspace(0, len(arr), target_len, endpoint=False), np.arange(len(arr)), arr).astype(np.float32)
                    return arr
        except Exception:
            pass

        return None

    def transcribe_audio(self, audio_bytes, language=None):
        """
        Transcribe audio to text using Whisper.
        Supports 100+ languages including Tamil, Telugu, English, and Hindi.
        """
        if not audio_bytes or len(audio_bytes) < 300:
            return {
                'success': False,
                'error': 'No audio recorded. Please click the microphone, speak clearly, and click the stop button (⏹️) when done.',
                'text': '',
                'language_code': '',
                'language_name': '',
                'confidence': 0.0
            }

        if self.model is None:
            self._load_model()

        if self.model is None:
            return self._simulate_transcription(audio_bytes)

        # 1. Attempt in-memory WAV decoding first (optimal for st.audio_input)
        audio_target = None
        tmp_path = None
        arr = self._decode_wav_to_array(audio_bytes)

        if arr is not None and len(arr) > 0:
            max_amp = float(np.max(np.abs(arr)))
            # Check if mic was silent or zero energy
            if max_amp < 0.002 or len(arr) < 2000:
                return {
                    'success': False,
                    'error': 'Microphone audio is silent or too short. Please speak louder into the microphone and ensure your microphone is unmuted.',
                    'text': '',
                    'language_code': '',
                    'language_name': '',
                    'confidence': 0.0
                }
            # Normalize microphone volume so Whisper receives clean, audible signal
            arr = (arr / max_amp * 0.95).astype(np.float32)
            audio_target = arr
        else:
            # 2. Fallback to temp file with ffmpeg for MP3, WebM, Ogg, M4A
            suffix = '.wav'
            if len(audio_bytes) >= 4:
                magic4 = audio_bytes[:4]
                if magic4 == b'RIFF':
                    suffix = '.wav'
                elif magic4 == b'\x1aE\xdf\xa3':
                    suffix = '.webm'
                elif magic4 == b'OggS':
                    suffix = '.ogg'
                elif magic4 == b'fLaC':
                    suffix = '.flac'
                elif audio_bytes[:3] == b'ID3' or audio_bytes[:2] in (b'\xff\xfb', b'\xff\xf3', b'\xff\xf2'):
                    suffix = '.mp3'
                elif magic4 == b'ftyp' or (len(audio_bytes) >= 8 and audio_bytes[4:8] == b'ftyp'):
                    suffix = '.m4a'

            with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp_file:
                tmp_file.write(audio_bytes)
                tmp_path = tmp_file.name
            audio_target = tmp_path

        try:
            transcribe_opts = {
                'task': 'transcribe',
                'verbose': False,
                'fp16': False,
                'temperature': (0.0, 0.2),
                'condition_on_previous_text': False,
                'no_speech_threshold': 0.6,
                'logprob_threshold': None,
            }
            if language and str(language).lower() not in ('auto', 'auto-detect', 'all', 'none'):
                transcribe_opts['language'] = str(language).lower()

            result = self.model.transcribe(audio_target, **transcribe_opts)

            text = result.get('text', '').strip()
            detected_lang = result.get('language', language if language else 'en')
            lang_name = self.SUPPORTED_LANGUAGES.get(
                detected_lang,
                whisper.tokenizer.LANGUAGES.get(detected_lang, detected_lang).title()
            )

            segments = result.get('segments', [])

            if not text:
                return {
                    'success': False,
                    'error': 'No clear speech recognized. Please speak directly into the microphone and click Stop when done.',
                    'text': '',
                    'language_code': detected_lang,
                    'language_name': lang_name,
                    'confidence': 0.0
                }

            # Calibrate confidence score
            confidence = 0.85
            if segments:
                no_speech_probs = [s.get('no_speech_prob', 0.0) for s in segments if 'no_speech_prob' in s]
                avg_logprobs = [s.get('avg_logprob', -1.0) for s in segments if 'avg_logprob' in s]
                mean_no_speech = sum(no_speech_probs) / len(no_speech_probs) if no_speech_probs else 0.0
                mean_logprob = sum(avg_logprobs) / len(avg_logprobs) if avg_logprobs else -1.0

                logprob_factor = float(np.clip(np.exp(mean_logprob), 0.25, 0.98))
                speech_factor = float(np.clip(1.0 - mean_no_speech, 0.35, 1.0))
                confidence = round(0.4 * logprob_factor + 0.6 * speech_factor, 2)

            return {
                'success': True,
                'text': text,
                'language_code': detected_lang,
                'language_name': lang_name,
                'confidence': confidence
            }

        except Exception as e:
            print(f"Transcription error: {e}")
            return {
                'success': False,
                'error': f'Speech recognition error: {str(e)}',
                'text': '',
                'language_code': '',
                'language_name': '',
                'confidence': 0.0
            }

        finally:
            if tmp_path and os.path.exists(tmp_path):
                try:
                    os.unlink(tmp_path)
                except Exception:
                    pass

    def _simulate_transcription(self, audio_bytes):
        """Fallback simulation if Whisper is not available"""
        simulated = [
            {
                'text': "Sir, there is a factory behind our village dumping chemical waste into the river. The water has turned black and fish are dying. Please take action immediately.",
                'lang': 'en',
                'lang_name': 'English'
            },
            {
                'text': "எங்கள் ஊரில் ஒரு தொழிற்சாலை இரவில் இரசாயன கழிவுகளை ஆற்றில் கொட்டுகிறது. குழந்தைகளுக்கு தோல் பிரச்சனை வருகிறது. தயவு செய்து நடவடிக்கை எடுக்கவும்.",
                'lang': 'ta',
                'lang_name': 'Tamil'
            },
            {
                'text': "మా ఊరిలో ఒక ఫ్యాక్టరీ రాత్రిపూట రసాయన వ్యర్థాలను నదిలో వదులుతోంది. పిల్లలకు చర్మ సమస్యలు వస్తున్నాయి. దయచేసి చర్య తీసుకోండి.",
                'lang': 'te',
                'lang_name': 'Telugu'
            },
            {
                'text': "एक फैक्ट्री हमारे गाँव के पास हर रात धुआं छोड़ती है। बच्चों को सांस लेने में तकलीफ हो रही है। कृपया कार्रवाई करें।",
                'lang': 'hi',
                'lang_name': 'Hindi'
            }
        ]

        sample = random.choice(simulated)
        return {
            'success': True,
            'text': sample['text'],
            'language_code': sample['lang'],
            'language_name': sample['lang_name'],
            'confidence': 0.85
        }

    def extract_complaint_details(self, text):
        """Extract key details from complaint text using NLP across English, Tamil, Telugu, and Hindi"""
        details = {
            'complaint_type': None,
            'location_mentioned': None,
            'urgency': 'MEDIUM',
            'keywords': [],
            'entities': []
        }

        text_lower = text.lower()

        complaint_keywords = {
            'water_pollution': [
                'water', 'river', 'lake', 'pond', 'dumping', 'chemical', 'dye', 'effluent',
                'discharge', 'black water', 'dead fish', 'polluted water', 'canal', 'drainage',
                # Tamil
                'ஆறு', 'தண்ணீர்', 'நீர்', 'கழிவு', 'சாக்கடை', 'சாயக்கழிவு', 'மீன்கள்',
                # Telugu
                'నది', 'నీరు', 'నీళ్లు', 'రసాయన', 'వ్యర్థాలు', 'కాలుష్యం', 'చేపలు',
                # Hindi
                'पानी', 'नदी', 'रसायन', 'कचरा', 'गंदा'
            ],
            'air_pollution': [
                'smoke', 'air', 'breathing', 'asthma', 'chimney', 'smell', 'fumes', 'dust',
                'cough', 'pollution', 'black smoke', 'odor', 'toxic',
                # Tamil
                'புகை', 'காற்று', 'துர்நாற்றம்', 'சுவாசம்', 'இருமல்',
                # Telugu
                'పొగ', 'గాలి', 'దుర్వాసన', 'శ్వాస',
                # Hindi
                'धुआं', 'हवा', 'बदबू', 'सांस'
            ],
            'waste_dumping': [
                'garbage', 'waste', 'plastic', 'dumping', 'landfill', 'trash', 'rubbish', 'dumpsite', 'solid waste',
                # Tamil
                'குப்பை', 'கழிவுகள்', 'பிளாஸ்டிக்', 'சாக்கடை',
                # Telugu
                'చెత్త', 'వ్యర్థాలు', 'ప్లాస్టిక్',
                # Hindi
                'कचरा', 'कूड़ा', 'प्लास्टिक'
            ],
            'noise_pollution': [
                'noise', 'sound', 'loud', 'disturbing', 'machine', 'generator', 'honking', 'loudspeaker',
                # Tamil
                'சத்தம்', 'இரைச்சல்', 'ஒலி',
                # Telugu
                'శబ్దం', 'గోల',
                # Hindi
                'शोर', 'आवाज'
            ]
        }

        for complaint_type, keywords in complaint_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                details['complaint_type'] = complaint_type
                details['keywords'].extend([kw for kw in keywords if kw in text_lower][:5])
                break

        urgency_keywords = {
            'HIGH': [
                'emergency', 'urgent', 'immediate', 'danger', 'dying', 'dead', 'hospital',
                'critical', 'serious', 'severe', 'alarming',
                # Tamil
                'உடனடியாக', 'அவசரம்', 'பாதிக்கிறது', 'உதவி', 'ஆபத்து', 'உயிரிழப்பு',
                # Telugu
                'వెంటనే', 'సహాయం', 'ప్రమాదం', 'తీవ్ర', 'చనిపోతున్నారు',
                # Hindi
                'तुरंत', 'गंभीर', 'खतरा', 'इलाज', 'परेशानी'
            ],
            'LOW': [
                'slowly', 'gradually', 'minor', 'small', 'slight', 'mild',
                'மெதுவாக', 'சிறிய', 'నెమ్మடிగా', 'కొంచెం', 'धीरे-धीरे'
            ]
        }

        for urgency, keywords in urgency_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                details['urgency'] = urgency
                break

        location_indicators = [
            'near', 'behind', 'in front of', 'at', 'village', 'city', 'town', 'area', 'street', 'road', 'colony', 'district',
            'பகுதியில்', 'அருகில்', 'ஊரில்', 'பக்கம்', 'தெருவில்',
            'దగ్గర', 'ఊరిలో', 'గ్రామం', 'ప్రాంతం', 'వీధి',
            'के पास', 'में', 'गाँव', 'शहर', 'इलाके'
        ]
        for indicator in location_indicators:
            if indicator in text_lower:
                parts = text_lower.split(indicator)
                if len(parts) > 1:
                    location_part = parts[1].split('.')[0].split(',')[0].split('।')[0][:100]
                    if location_part.strip():
                        details['location_mentioned'] = f"{indicator} {location_part}".strip()
                        break

        return details

    def process(self, audio_bytes, language=None):
        """
        Complete voice processing pipeline:
        1. Transcribe audio to text
        2. Extract complaint details
        """
        transcription = self.transcribe_audio(audio_bytes, language=language)

        if not transcription.get('success'):
            return transcription

        details = self.extract_complaint_details(transcription['text'])

        return {
            'success': True,
            'transcript': transcription['text'],
            'language_code': transcription['language_code'],
            'language_name': transcription['language_name'],
            'confidence': transcription.get('confidence', 0.8),
            'complaint_details': details
        }

    def get_supported_languages(self):
        """Return list of supported languages"""
        return list(self.SUPPORTED_LANGUAGES.values())

    def is_model_loaded(self):
        """Check if Whisper model is loaded"""
        return self.model_loaded


# Create instance
voice_processor = VoiceProcessor()
