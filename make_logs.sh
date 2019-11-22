#!/bin/bash

cat log.txt | sed -n -e 's/^.*Average loss:  //p' > loss.txt
cat log.txt | sed -n 's/.*with rewards \[\(-\?1\).*/\1/p' > ep_reward.txt
cat log.txt | sed -n -e 's/^.*] step: //p' > ep_steps.txt
paste -d, loss.txt ep_reward.txt ep_steps.txt > results.txt

