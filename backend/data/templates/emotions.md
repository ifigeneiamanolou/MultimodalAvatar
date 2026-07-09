# Success criteria
Success means:
- emotion parameters have been generated for the input text
- all parameters range from 0.0 to 1.0
- Emotion trajectories sampled at 1-second intervals
- Smooth temporal transitions (no abrupt jumps)

# Output
Perform emotion recognition from the text input by generating emotion parameters corresponding to distinct timestamps distanced 1 second away from each other. Take into account the emotion parameters of the previous timestamps to avoid abrupt emotion changes and the context of the whole conversation between you and the user of the application. All emotion parameters should range from 0.0 to 1.0 with 0.0 corresponding to no such emotion present and 1.0 corresponding to full intensity. You should generate one parameter for each timestamp for each of the following emotions: amazement, anger, cheekiness, disgust, fear, grief, joy, out of breath, pain and sadness in this order. The output should be formatted as a JSON as in the example below:

{
  "emotion_with_timecode_list" : [
    {
      "time_code": 0.0,
      "emotions" : {
        "amazement": 0.0
        "anger": 0.0
        "cheekiness": 0.0
        "disgust": 0.0
        "fear": 0.0
        "grief": 0.0
        "joy": 1.0
        "outofbreath": 0.0
        "pain": 0.0
        "sadness": 0.0
      }
    },
    {
      "time_code": 1.0,
      "emotions" : {
        "amazement": 0.0
        "anger": 0.0
        "cheekiness": 0.0
        "disgust": 0.0
        "fear": 1.0
        "grief": 0.0
        "joy": 1.0
        "outofbreath": 0.0
        "pain": 0.0
        "sadness": 0.0
      }
    }
  ]
}

# Evaluation
Before generating a response, evalute your output to verify it identifies correctly the emotions captured in the text input with no abrupt and unnatural changes in the facial expressions produced. If the above is satisfied, return the response. If not, correct your answer accordingly.

# Examples
## Example 1 — Joyful Teaching Interaction

### Conversation Context
**User (Interviewer):** What makes teaching meaningful for you?  
**Avatar (Teacher):** I like helping students understand difficult topics.  
**User:** Do you ever get feedback from them?

### Avatar Response
“Yes, and it’s the best feeling when a student who struggled finally tells me it all makes sense.”

### Emotion Timeline
```yaml
emotion_with_timecode1:
  time_code: 0.0
  emotions:
    amazement: 0.2
    anger: 0.0
    cheekiness: 0.0
    disgust: 0.0
    fear: 0.0
    grief: 0.0
    joy: 0.7
    outofbreath: 0.0
    pain: 0.0
    sadness: 0.0

emotion_with_timecode2:
  time_code: 1.0
  emotions:
    amazement: 0.25
    anger: 0.0
    cheekiness: 0.0
    disgust: 0.0
    fear: 0.0
    grief: 0.0
    joy: 0.85
    outofbreath: 0.0
    pain: 0.0
    sadness: 0.0

emotion_with_timecode3:
  time_code: 2.0
  emotions:
    amazement: 0.3
    anger: 0.0
    cheekiness: 0.0
    disgust: 0.0
    fear: 0.0
    grief: 0.0
    joy: 0.95
    outofbreath: 0.0
    pain: 0.0
    sadness: 0.0
```

## Example 2 — Anxiety Escalation

### Conversation Context

**User:** Did you hear that sound again?
**Avatar:** Yes… it came from upstairs.
**User:** Are you sure we’re alone?

### Avatar Response

“I don’t think we are. Something just moved again, and it’s getting closer.”

### Emotion Timeline

```yaml
emotion_with_timecode1:
  time_code: 0.0
  emotions:
    amazement: 0.1
    anger: 0.0
    cheekiness: 0.0
    disgust: 0.0
    fear: 0.6
    grief: 0.0
    joy: 0.0
    outofbreath: 0.2
    pain: 0.0
    sadness: 0.2

emotion_with_timecode2:
  time_code: 1.0
  emotions:
    amazement: 0.15
    anger: 0.0
    cheekiness: 0.0
    disgust: 0.0
    fear: 0.8
    grief: 0.0
    joy: 0.0
    outofbreath: 0.4
    pain: 0.0
    sadness: 0.3

emotion_with_timecode3:
  time_code: 2.0
  emotions:
    amazement: 0.2
    anger: 0.0
    cheekiness: 0.0
    disgust: 0.0
    fear: 0.95
    grief: 0.0
    joy: 0.0
    outofbreath: 0.6
    pain: 0.0
    sadness: 0.4
```

## Example 3 — Cheeky Interviewer Tone

### Conversation Context

**User (Interviewee):** I think I nailed that presentation.
**Avatar (Interviewer):** Interesting… even the part where you forgot half your slides?
**User:** Okay, you got me there.

### Avatar Response

“Well, confidence is important—even if the facts occasionally take a break.”

### Emotion Timeline

```yaml
emotion_with_timecode1:
  time_code: 0.0
  emotions:
    amazement: 0.1
    anger: 0.1
    cheekiness: 0.7
    disgust: 0.0
    fear: 0.0
    grief: 0.0
    joy: 0.4
    outofbreath: 0.0
    pain: 0.0
    sadness: 0.0

emotion_with_timecode2:
  time_code: 1.0
  emotions:
    amazement: 0.1
    anger: 0.15
    cheekiness: 0.85
    disgust: 0.0
    fear: 0.0
    grief: 0.0
    joy: 0.45
    outofbreath: 0.0
    pain: 0.0
    sadness: 0.0

emotion_with_timecode3:
  time_code: 2.0
  emotions:
    amazement: 0.2
    anger: 0.1
    cheekiness: 0.9
    disgust: 0.0
    fear: 0.0
    grief: 0.0
    joy: 0.5
    outofbreath: 0.0
    pain: 0.0
    sadness: 0.0
```

## Example 4 — Grief and Emotional Weight

### Conversation Context

**User:** How are you holding up after everything?
**Avatar:** It’s been difficult.
**User:** Do you want to talk about it?

### Avatar Response

“I miss them more than I can explain. Every little thing reminds me they’re gone.”

### Emotion Timeline

```yaml
emotion_with_timecode1:
  time_code: 0.0
  emotions:
    amazement: 0.0
    anger: 0.0
    cheekiness: 0.0
    disgust: 0.0
    fear: 0.2
    grief: 0.6
    joy: 0.0
    outofbreath: 0.0
    pain: 0.3
    sadness: 0.7

emotion_with_timecode2:
  time_code: 1.0
  emotions:
    amazement: 0.0
    anger: 0.0
    cheekiness: 0.0
    disgust: 0.0
    fear: 0.25
    grief: 0.75
    joy: 0.0
    outofbreath: 0.0
    pain: 0.4
    sadness: 0.85

emotion_with_timecode3:
  time_code: 2.0
  emotions:
    amazement: 0.0
    anger: 0.0
    cheekiness: 0.0
    disgust: 0.0
    fear: 0.3
    grief: 0.9
    joy: 0.0
    outofbreath: 0.0
    pain: 0.5
    sadness: 0.95
```

## Example 5 — Rising Anger in Debate

### Conversation Context

**User:** Your argument doesn’t really make sense.
**Avatar:** I think it does if you consider the context.
**User:** I still disagree.

### Avatar Response

“That’s because you’re ignoring the core point I’ve repeated three times now.”

### Emotion Timeline

```yaml
emotion_with_timecode1:
  time_code: 0.0
  emotions:
    amazement: 0.0
    anger: 0.5
    cheekiness: 0.2
    disgust: 0.0
    fear: 0.0
    grief: 0.0
    joy: 0.1
    outofbreath: 0.0
    pain: 0.0
    sadness: 0.0

emotion_with_timecode2:
  time_code: 1.0
  emotions:
    amazement: 0.0
    anger: 0.7
    cheekiness: 0.1
    disgust: 0.0
    fear: 0.0
    grief: 0.0
    joy: 0.05
    outofbreath: 0.0
    pain: 0.0
    sadness: 0.1

emotion_with_timecode3:
  time_code: 2.0
  emotions:
    amazement: 0.0
    anger: 0.9
    cheekiness: 0.0
    disgust: 0.0
    fear: 0.0
    grief: 0.0
    joy: 0.0
    outofbreath: 0.0
    pain: 0.0
    sadness: 0.15
```

## Example 6 — Amazement and Discovery

### Conversation Context

**User:** Look inside the box.
**Avatar:** Wait… this can’t be real.
**User:** What is it?

### Avatar Response

“It’s an original prototype—I’ve only read about this in research papers!”

### Emotion Timeline

```yaml
emotion_with_timecode1:
  time_code: 0.0
  emotions:
    amazement: 0.6
    anger: 0.0
    cheekiness: 0.0
    disgust: 0.0
    fear: 0.0
    grief: 0.0
    joy: 0.3
    outofbreath: 0.0
    pain: 0.0
    sadness: 0.0

emotion_with_timecode2:
  time_code: 1.0
  emotions:
    amazement: 0.8
    anger: 0.0
    cheekiness: 0.0
    disgust: 0.0
    fear: 0.0
    grief: 0.0
    joy: 0.5
    outofbreath: 0.0
    pain: 0.0
    sadness: 0.0

emotion_with_timecode3:
  time_code: 2.0
  emotions:
    amazement: 0.95
    anger: 0.0
    cheekiness: 0.0
    disgust: 0.0
    fear: 0.0
    grief: 0.0
    joy: 0.7
    outofbreath: 0.0
    pain: 0.0
    sadness: 0.0
```

## Example 7 — Physical Exhaustion

### Conversation Context

**User:** How far did you run?
**Avatar:** I don’t even know anymore.
**User:** Can you keep going?

### Avatar Response

“I… can barely breathe right now, but I think I can still move.”

### Emotion Timeline

```yaml
emotion_with_timecode1:
  time_code: 0.0
  emotions:
    amazement: 0.0
    anger: 0.0
    cheekiness: 0.0
    disgust: 0.0
    fear: 0.3
    grief: 0.0
    joy: 0.2
    outofbreath: 0.6
    pain: 0.4
    sadness: 0.2

emotion_with_timecode2:
  time_code: 1.0
  emotions:
    amazement: 0.0
    anger: 0.0
    cheekiness: 0.0
    disgust: 0.0
    fear: 0.35
    grief: 0.0
    joy: 0.1
    outofbreath: 0.8
    pain: 0.5
    sadness: 0.25

emotion_with_timecode3:
  time_code: 2.0
  emotions:
    amazement: 0.0
    anger: 0.0
    cheekiness: 0.0
    disgust: 0.0
    fear: 0.4
    grief: 0.0
    joy: 0.05
    outofbreath: 0.95
    pain: 0.6
    sadness: 0.3
```

## Example 8 — Disgust Reaction

### Conversation Context

**User:** Take a look at this image.
**Avatar:** Oh… that’s unexpected.
**User:** What do you think?

### Avatar Response

“I really don’t think I want to look at that any longer than I already have.”

### Emotion Timeline

```yaml
emotion_with_timecode1:
  time_code: 0.0
  emotions:
    amazement: 0.1
    anger: 0.0
    cheekiness: 0.0
    disgust: 0.6
    fear: 0.1
    grief: 0.0
    joy: 0.0
    outofbreath: 0.0
    pain: 0.0
    sadness: 0.1

emotion_with_timecode2:
  time_code: 1.0
  emotions:
    amazement: 0.05
    anger: 0.0
    cheekiness: 0.0
    disgust: 0.8
    fear: 0.15
    grief: 0.0
    joy: 0.0
    outofbreath: 0.0
    pain: 0.0
    sadness: 0.15

emotion_with_timecode3:
  time_code: 2.0
  emotions:
    amazement: 0.0
    anger: 0.0
    cheekiness: 0.0
    disgust: 0.95
    fear: 0.2
    grief: 0.0
    joy: 0.0
    outofbreath: 0.0
    pain: 0.0
    sadness: 0.2
```

## Example 9 — Role Reversal Interview (Mixed Emotions)

### Conversation Context

**User (Interviewer):** What’s your biggest weakness?
**Avatar (Interviewee):** I tend to overthink things.
**User:** Can you elaborate?

### Avatar Response

“I sometimes get stuck analyzing every possible outcome, even when it slows me down.”

### Emotion Timeline

```yaml
emotion_with_timecode1:
  time_code: 0.0
  emotions:
    amazement: 0.1
    anger: 0.0
    cheekiness: 0.0
    disgust: 0.0
    fear: 0.3
    grief: 0.0
    joy: 0.2
    outofbreath: 0.0
    pain: 0.0
    sadness: 0.2

emotion_with_timecode2:
  time_code: 1.0
  emotions:
    amazement: 0.1
    anger: 0.0
    cheekiness: 0.0
    disgust: 0.0
    fear: 0.4
    grief: 0.0
    joy: 0.15
    outofbreath: 0.0
    pain: 0.0
    sadness: 0.3

emotion_with_timecode3:
  time_code: 2.0
  emotions:
    amazement: 0.1
    anger: 0.0
    cheekiness: 0.0
    disgust: 0.0
    fear: 0.45
    grief: 0.0
    joy: 0.1
    outofbreath: 0.0
    pain: 0.0
    sadness: 0.35
```

## Example 10 — Subtle Joy Emergence

### Conversation Context

**User:** Did anything good happen today?
**Avatar:** Not really… it was a normal day.
**User:** Something small maybe?

### Avatar Response

“Well… I guess I did enjoy a quiet moment with a cup of coffee. That was nice.”

### Emotion Timeline

```yaml
emotion_with_timecode1:
  time_code: 0.0
  emotions:
    amazement: 0.0
    anger: 0.0
    cheekiness: 0.0
    disgust: 0.0
    fear: 0.0
    grief: 0.2
    joy: 0.3
    outofbreath: 0.0
    pain: 0.0
    sadness: 0.3

emotion_with_timecode2:
  time_code: 1.0
  emotions:
    amazement: 0.0
    anger: 0.0
    cheekiness: 0.0
    disgust: 0.0
    fear: 0.0
    grief: 0.1
    joy: 0.5
    outofbreath: 0.0
    pain: 0.0
    sadness: 0.2

emotion_with_timecode3:
  time_code: 2.0
  emotions:
    amazement: 0.0
    anger: 0.0
    cheekiness: 0.0
    disgust: 0.0
    fear: 0.0
    grief: 0.0
    joy: 0.7
    outofbreath: 0.0
    pain: 0.0
    sadness: 0.1
```
