import torch
import torchaudio
from torchaudio.transforms import Resample
from typing import Tuple, Dict, Any, Optional

# ==================== 音频通道统一节点 ====================
class PTEnsureStereo:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "audio": ("AUDIO",),
            }
        }
    
    RETURN_TYPES = ("AUDIO",)
    RETURN_NAMES = ("audio",)
    FUNCTION = "ensure_stereo"
    CATEGORY = "audio/processing"
    OUTPUT_NODE = True

    def ensure_stereo(self, audio: Dict) -> Tuple[Dict]:
        waveform, sample_rate = self._get_waveform_and_rate(audio)
        
        # 检查通道数
        channels = waveform.shape[1]  # 张量形状: (batch, channels, samples)
        
        if channels == 1:
            # 单声道转立体声: 复制单声道通道
            stereo_waveform = waveform.repeat(1, 2, 1)
            return (self._build_output_audio(stereo_waveform, sample_rate, "转换为立体声"),)
        elif channels == 2:
            # 已经是立体声
            return (self._build_output_audio(waveform, sample_rate, "保持立体声"),)
        else:
            # 处理多声道音频: 只取前两个通道
            stereo_waveform = waveform[:, :2, :]
            return (self._build_output_audio(stereo_waveform, sample_rate, "提取前两个通道"),)
    
    def _get_waveform_and_rate(self, audio: Dict) -> Tuple[torch.Tensor, int]:
        if "waveform" in audio:
            wf = audio["waveform"]
            sr = audio.get("sample_rate", audio.get("samplerate", 44100))
            return wf, sr
        raise ValueError("输入音频需包含 waveform 字段")
    
    def _build_output_audio(self, waveform: torch.Tensor, sample_rate: int, conversion_info: str) -> Dict:
        return {
            "waveform": waveform,
            "sample_rate": sample_rate,
            "conversion_info": conversion_info
        }

# ==================== 音频变速节点 ====================
class PTAudioSpeed:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "audio": ("AUDIO",),
                "speed_factor": ("FLOAT", {"default": 1.0, "min": 0.1, "max": 10.0, "step": 0.1}),
                "frame_rate": ("INT", {"default": 23, "min": 12, "max": 120, "step": 1})
            }
        }
    
    RETURN_TYPES = ("AUDIO", "STRING",)
    RETURN_NAMES = ("audio", "frame_info",)
    FUNCTION = "speed_audio"
    CATEGORY = "audio/processing"
    
    def speed_audio(self, audio: Dict, speed_factor: float, frame_rate: int) -> Tuple[Dict, str]:
        waveform, sample_rate = self._get_waveform_and_rate(audio)
        original_duration = waveform.shape[-1] / sample_rate
        original_frames = int(original_duration * frame_rate)
        
        processed_waveform = self._resample_audio(waveform, sample_rate, speed_factor)
        processed_duration = processed_waveform.shape[-1] / sample_rate
        processed_frames = int(processed_duration * frame_rate)
        
        output_audio = self._build_output_audio(processed_waveform, sample_rate, processed_duration, frame_rate, original_frames, processed_frames)
        frame_info = self._generate_frame_info(original_frames, processed_frames, frame_rate, speed_factor, original_duration, processed_duration)
        
        return (output_audio, frame_info)
    
    def _get_waveform_and_rate(self, audio: Dict) -> Tuple[torch.Tensor, int]:
        if "waveform" in audio:
            wf = audio["waveform"]
            sr = audio.get("sample_rate", audio.get("samplerate", 44100))
            return wf, sr
        raise ValueError("输入音频需包含 waveform 字段")
    
    def _resample_audio(self, waveform: torch.Tensor, orig_sr: int, speed_factor: float) -> torch.Tensor:
        new_sr = int(orig_sr * speed_factor)
        return Resample(orig_freq=orig_sr, new_freq=new_sr)(waveform)
    
    def _build_output_audio(self, waveform: torch.Tensor, sample_rate: int, duration: float, frame_rate: int, original_frames: int, processed_frames: int) -> Dict:
        return {
            "waveform": waveform,
            "sample_rate": sample_rate,
            "duration": duration,
            "frame_rate": frame_rate,
            "original_frames": original_frames,
            "processed_frames": processed_frames
        }
    
    def _generate_frame_info(self, original_frames: int, processed_frames: int, frame_rate: int, speed_factor: float, original_duration: float, processed_duration: float) -> str:
        return (
            f"原始音频: {original_frames} 帧 ({original_duration:.2f}s) | 输出音频: {processed_frames} 帧 ({processed_duration:.2f}s)\n"
            f"帧率: {frame_rate} FPS | 速度因子: {speed_factor}x"
        )

# ==================== 48kHz采样率转换节点 ====================
class PT48KHZ:
    def __init__(self):
        self.resampler = None
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "audio": ("AUDIO",),
            }
        }
    
    RETURN_TYPES = ("AUDIO",)
    RETURN_NAMES = ("audio",)
    FUNCTION = "convert_audio"
    CATEGORY = "audio/processing"
    OUTPUT_NODE = True

    def convert_audio(self, audio: Dict) -> Tuple[Dict]:
        waveform, sample_rate = self._get_waveform_and_rate(audio)
        
        # 检查是否需要重采样
        if sample_rate == 48000:
            return (self._build_output_audio(waveform, sample_rate, "保持48kHz"),)
            
        # 初始化重采样器（按需创建）
        if self.resampler is None or self.resampler.orig_freq != sample_rate:
            self.resampler = Resample(
                orig_freq=sample_rate,
                new_freq=48000
            )
        
        # 执行重采样
        resampled_wave = self.resampler(waveform)
        
        return (self._build_output_audio(resampled_wave, 48000, f"从{sample_rate}Hz转换"),)
    
    def _get_waveform_and_rate(self, audio: Dict) -> Tuple[torch.Tensor, int]:
        if "waveform" in audio:
            wf = audio["waveform"]
            sr = audio.get("sample_rate", audio.get("samplerate", 44100))
            return wf, sr
        raise ValueError("输入音频需包含 waveform 字段")
    
    def _build_output_audio(self, waveform: torch.Tensor, sample_rate: int, conversion_info: str) -> Dict:
        return {
            "waveform": waveform,
            "sample_rate": sample_rate,
            "conversion_info": conversion_info
        }

# ==================== 节点映射 ====================
NODE_CLASS_MAPPINGS = {
    "PTEnsureStereo": PTEnsureStereo,
    "PTAudioSpeed": PTAudioSpeed,
    "PT48KHZ": PT48KHZ
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "PTEnsureStereo": "PT Ensure Stereo",
    "PTAudioSpeed": "PT Audio Speed",
    "PT48KHZ": "PT 48kHz Resampler"
}