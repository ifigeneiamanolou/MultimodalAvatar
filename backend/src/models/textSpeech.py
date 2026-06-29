import whisperx
import boto3            # AWS SDK for Python

# ============== Settings =================
deviceAlign = "cpu"
compute_type = "int8"

# Force alignment WhisperX client
model_align, metadata = whisperx.load_align_model(language_code = "en", device = deviceAlign, compute_type = compute_type)

# Audio transcription model instance

# SageMaker AI runtime client
sagemaker_runtime = boto3.runtime("sagemaker-runtime", region_name = 'aws_region')      # TO FILL IN THE CORRECT AWS REGION
