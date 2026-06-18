## File structure

The data folder contains three main sections:

* raw ==> includes raw data, meaning the recorded user input in "audio-[number].webm" format and the text response from the LLM in "response-[number].txt" format
* processed ==> includes processed files, meaning the transcription of the user input in "transcription-[number].txt" format and the response of the LLM after TTS (using ElevenLabs model) in "tts-[number].mp3" format. It also includes files containing the phonemes, the visemes and the ArtKit blendshapes to render the facial animation from the bot audio response in "phonemes-[number].json", "visemes-[number].json" and "artkit-[number].json" format respectively.
* feedback ==> includes a JSON file for each user-bot conversation to be fed into the model used to provide feedback to the user (through prompt engineering)

It also includes a csv file containing the phoneme to ArtKit coefficient mappings. Each phoneme in this file, corresponds to a value for every single coefficient. To note that this mapping doesn't integrate emotion into the expressions. These are then mapped to a face rig by UE5. 

## Phonemes and ArtKit coefficients
Phonemes are the smallest units of language that can distinguish words from each other broken into consonants and vowels (39 in total). Apples ArtKit 52 facial blendshapes or "morph targets" control specific parts of facial motion and range from 0.0 (neutral state) to 1.0.

## Future improvements 
The phonemes derived from the text generated during TTS should be cached, to reduce latency while using the application (especially if a training stage is added for the specific use cases of the application).

