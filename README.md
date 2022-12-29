## TARDes: Test Assignment Results Description

As a person, who is not much experienced with the NLP tasks and models, I separated the task into three parts.
First, I aimed to explore different parameters of the training independently, and how they affect the training in a short run.
Second, I tried a prolonged training routine, to tune parameters that affect the training in a longer run or do not work good together.
Third, I've planned for further experiments (virtual in this case, since the time is up, but that's part of the task as I understand it).

Technical details:
- I separated the provided notebook into three parts: 
    - data preparation and package installation moved into a separate notebook [preparation.ipynb](preparation.ipynb);
    - part of helper functions moved to a python file [helper.py](helper.py);
    - all configs, execution, and some definitions left in the main notebook.
  For each experiment I tried to spawn separate notebook, which is a copy of the baseline, with minimal modifications made.
- To track the results I used wandb, so here's my project [JB_test](https://wandb.ai/martslaaf/JB_test).

Before anything, here's my [baseline run](baseline.ipynb). The result on the test set was 

| metric | value |
| - | - |
| eval_precision | 0.39|
| eval_recall | 0.24|
| eval_f1 | 0.29|


### Short Run Experiments

1. Constant LR instead of linearly decreasing one. It's definitely useful to decrease LR on a very long run, but for the short one it makes training simply stagnate in the nearest local minimum. Conclusion: unless constant LR stagnates, I would avoid decreasing LR. The code is saved in [constant_lr](constant_lr.ipynb). The corresponding run token in wandb is `constant_lr`.
1. Higher LR, since the default is somewhat low-ish for an outside person. I mean, it's a default value for a reason, I guess. Yet I would expect it to be an order of magnitude higher. I've tried 3e-4 and 4e-3. The first working better, and the second worser than the initial one. Conclusion: it looks reasonable to have higher LR. The code is in [higher_lr](higher_lr.ipynb). The wandb tokens are `3e-4` and `4e-3`.
1. Longer input sequence. I noticed, that the input is cropped at the range of 128 tokens. And that in dataset, there's around 24% of the inputs that are longer. So, I've tried to increase the size of the input, which provided very small increase in the result. I guess, while it's not harming, why not to have it. Code in the [longer_input](longer_input.ipynb), results in `longer_sequence`.
1. More hidden layers in the decoder. As obvious as it is -- the more layers, the better. I stopped at 32, but it can go further, I guess. Conclusion: at least 32 hidden layers recommended. Finding optimal count is left for futrther investigation. Code is in [decoder_hidden_layers](decoder_hidden_layers.ipynb), results are in the `HL=24`, `HL=32` and `HL=64` runs in wandb.
1. More attention heads. Strangely enough, it's almost no change (if not decreasing). Confusing results, should read more about it. Chances are, it requires longer training time to engage, or something like that. Yet again, left for further investigation. Code is in [decoder_num_attention_heads](decoder_num_attention_heads.ipynb), results are in `NA=32` and `NA=16`.
1. Larger intermediate state in decoder. Increasing intermediate state of the decoder provides quite small but somewhat stable boost. I don't think this is important, but since I have a tad of a spare GPU memory, I would try to compare the results on the longer run, it may have some small advantage. Code is in [decoder_intermediate](decoder_intermediate.ipynb), results are in `IS=2048` and `IS=4096`.
1. Hidden layer dropout. Since the train and valid loaders had quite different results (though both stabely decreasing in the short run), I hoped to bring them closer together with increasing the dropout rate. However, it produced controversial results in a short run and was left for longer runs. [hidden_dropout](hidden_dropout.ipynb), `hidden_drop=0.2`.

### Long Run Experiments

After set of previous explorative experiments was finished, I started longer runs. The code is in the [all_capacity_together](all_capacity_together.ipynb). Further, I will document some specific runs.

1. First of all, I've just run all capacity increasing tricks together. Results are in the run `altogether`.
1. As I've noted probable signs of overfitting, I've added a tad of weight decay (0.02). The results are in the run `altogether + wd`. As it is shown in the run with higher weight decay -- it doesn't provide much better results, so I left it on low settings further.
1. I've increased the epochs of training to 10 epochs, where first sure signs of overfitting were notable. One can see this in the `at, wd, long` results in wandb.
1. Finally, after making several steps, I've finished with what presented in the `final` run in wandb. At this point I ran the test once again, so the final results on test are:

| metric | value |
| - | - |
| eval_precision | 0.46 |
| eval_recall | 0.47 |
| eval_f1 | 0.45 |

### Unsolved Quests and Further Plans

Since the time of the work was limited to basically one working day, I've limited myself to operating with known things mostly. However, I have several further things I would go to explore, should it be real task. Here they go.

- **Hyper-Parameter selection and tuning.** I have several parameters, which are problematic to fit together by hand. Should it be practical task -- parameter selection can be an important stage to win some quality.
- **Employ a pre-trained initialization.** I guess, starting training from the pre-trained checkpoint is the next go-to. I haven't had time to varefully look through documentation and search for how to do it in the huggingface transformers. But this is definitely in the bucketlist.
- **Understanding seemingly random fails.** I have noted several seemingly random fails (logged as `failed_long`). It looks as at some point there are problems with gradient or something like that. I've read that there are strategies to mitigate this. It is easy to see, that this happens in places, when the train loss jumps up. One strategy is to revert to the previous checkpoint in case of such situation. But also, these errors misteriously disappeared after I cleaned logs. Dunno, need to investigate.
- **Imbalance of the length** is strong in this task. I mean, the output is way smaller than input. I would go to read about it, maybe there are some ways to benefit from it. For outsider it looks like if one has a small and fixed maximum length of prediction with kinda strict notation (I mean, name of the function is far away from random text), it could be beneficial to avoid burdens of the sequence prediction, and to predict it in a straighter way.
- **Why the results are so different for train and validation?** I mean even the loss values themselve. I guess, it may be because of the small dataset size, so the model can quickly remember some names. Though, even with this in mind, it looks a bit strange to me, as a CV person.
- **Figure out augmentation.** While for the input augmentation could be more problematic and less important (we have the pre-trained encoder that was trained on a larger dataset ~~by smarter guys~~), the augmentation of the target could be a good idea. After all, functions "generate text" and "produce text" are, probably, somewhat close. 