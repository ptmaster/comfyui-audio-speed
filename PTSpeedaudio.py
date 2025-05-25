import torch
import torchaudio
from torchaudio.transforms import Resample
from typing import Tuple, Dict, Any

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
            return wf.unsqueeze(0) if wf.dim() == 1 else wf, sr
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

NODE_CLASS_MAPPINGS = {
    "PTAudioSpeed": PTAudioSpeed
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "PTAudioSpeed": "PT Audio Speed"
}