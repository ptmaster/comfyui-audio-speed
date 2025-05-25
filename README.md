# comfyui-audio-speed
comfyui-audio-speed
When using FantasyTalking for voiceovers with WAN (Tongyi Wanxiang Video Model), I noticed it only supports 23FPS audio frame rates while I typically work in 16FPS environments. I conceived an approach: feeding the sampler with audio accelerated by 1.4x (23/16 ratio), then importing the original audio during final video rendering. However, since ComfyUI currently lacks native audio speed adjustment nodes, I developed a custom solution. This self-made node defaults to 0.7x speed (equivalent to 1.4x acceleration) for audio processing.
Of course, you can also utilize it as a universal audio speed adjustment node for any desired speed modification.
