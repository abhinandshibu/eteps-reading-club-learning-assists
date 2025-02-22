This script generates resources such as summaries and flashcards to support learning in the ETEPS Reading Club.

More information about the reading club can be found here: https://abhinandshibu.com/ETEPS+Reading+Club

In a `.env` file, please make the environment variable(s): 
* `OPENAI_API_KEY`

TODO: 
* Improve prompts to generate the summary and flashcards
* Have two summaries generated, one short 1 paragraph overview and another detailed overview 
* Allow the user to the enter the topic and the specific reading 
* Prompt the LLM to initially fetch its own information about the topic and the specific reading, and append it to its own context, so further generations can be grounded in this reading related information
* Human-AI teaming approach, where the slides & flashcards can be reviewed with suggested edits, or regeneration can be requested.
* Use reasoning models to produce the summary and flashcards from the transcripts 
* Be able to input the slides (or text of discussion questions) guiding the discussion, so the LLM can be grounded on the scaffolding intention
* (MAYBE) Get the transcripts to be outputted in a nicer / easier to parse manner for the LLM, might improve quality of insights deciphered
* (MAYBE) Come up with a scaffolded multi-step approach to aid the LLM in deciphering particular kinds of insights from the conversation

