import torch
try:
	torch.cuda.empty_cache()
except Exception as e:
	print(f"Error : {e}")
