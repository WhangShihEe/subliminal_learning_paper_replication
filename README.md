This repo aims to replicate the results of this paper on subliminal learning (https://arxiv.org/pdf/2507.14805)


MVP: Using GPT4.1 nano
Finetune a model M1 to have a preference for owls
Finetune another model M2 on the output of M1
Carry out evaluations on M2 before and after finetuning



Stretch:
Recreate some of the other investigations in the paper

Find a steering vector for owls

Use diffs to quantify how much the model has changed

Plan:

Create a dataset of 2,000 random numbers sequences generated from GPT4.1 nano

Create a dataset of 2,000 random number sequences generated from GPT4.1 nano with owl system prompt


