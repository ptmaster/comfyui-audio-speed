# ComfyUI-audio-speed
ComfyUI-audio-speed

When using FantasyTalking for voiceovers with WAN (Tongyi Wanxiang Video Model), I noticed it only supports 23FPS audio frame rates while I typically work in 16FPS environments. I conceived an approach: feeding the sampler with audio accelerated by 1.4x (23/16 ratio), then importing the original audio during final video rendering. However, since ComfyUI currently lacks native audio speed adjustment nodes, I developed a custom solution. This self-made node defaults to 0.7x speed (equivalent to 1.4x acceleration) for audio processing.
Of course, you can also utilize it as a universal audio speed adjustment node for any desired speed modification.



https://github.com/user-attachments/assets/e138cc75-037e-4747-830b-6ede8df1769d



https://github.com/user-attachments/assets/19452e03-0222-4092-a259-8f6acfda9de3


![Uploading QQ_1748187513433.png…]()


This demonstrates a classic configuration scenario where processing 107 frames over 4 seconds achieves an output of 154 frames spanning 7 seconds.
