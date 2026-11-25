# Archived round logs

These files reproduce Tables 1–3 and 5 of the manuscript without retraining. They contain
per-image correctness predictions, per-round action indices and AETTA-style logs; they do
not contain CIFAR images. The CIFAR-10-C and CIFAR-100-C corpora are public.

The data are released under CC BY 4.0; the code is MIT.

| File | Contents | SHA-256 |
|---|---|---|
| `archived/cifar10_r18/arms_holdout_deploy_per_image.npz` | CIFAR-10-C / ResNet-18 per-image W and V predictions | `f7f17b97c934fefa1f93dd8633a263a1d7a60f4e7681d59713d403081b4976b8` |
| `archived/cifar10_r18/arms_holdout_deploy_arms.csv` | CIFAR-10-C / ResNet-18 per-round action log | `0ea66d137466500d1216ff6b00b63d2dac2d727786456fd00cd7f030168cfadb` |
| `archived/cifar10_r50/confirm_resnet50_per_image.npz` | CIFAR-10-C / ResNet-50 per-image W and V predictions | `9c90f77603ffe9886c15a38d36e7f585392fbc37c6435f83a1bb6340da0d4b77` |
| `archived/cifar10_r50/confirm_resnet50_arms.csv` | CIFAR-10-C / ResNet-50 per-round action log | `d8c9977fddfea22d9fdbf760846c08238ba284e57ba93bccfa191af97d06a591` |
| `archived/cifar100_r18/arms_holdout_c100_per_image.npz` | CIFAR-100-C / ResNet-18 per-image W and V predictions | `f396b197257a18f49a14531d450e20d6b4b3c09a760e27f2e30cd5b798b774e2` |
| `archived/cifar100_r18/arms_holdout_c100_arms.csv` | CIFAR-100-C / ResNet-18 per-round action log | `22ff3ab3394702acd943cc381eb51739bdfb1043bf3e7edaaa46444964a970cd` |
| `archived/aetta/aetta_src_750_rounds.csv` | CIFAR-10-C AETTA-style source-calibrated log | `3fac9f852207195913f9e5639efbd64fd38ac7c27b7dde3056a7f3fae3255621` |
| `archived/aetta/aetta_tgt_750_paired_rounds.csv` | CIFAR-10-C AETTA-style target-calibrated paired log | `cb2123100cee81f4b053c8951ac470c593e1cf552e8c944a330501eeab9755e7` |
| `archived/aetta/aetta_v3_750_rounds.csv` | CIFAR-10-C earlier target-calibrated AETTA log | `fd16ae782d04cb62a993a0b43d32deacf1c6d355e2954c0e3173adb78603ef4c` |
| `archived/aetta/aetta_c100_750_rounds.csv` | CIFAR-100-C AETTA-style source-calibrated log | `ccd0c64d0bd92f2a803fcf30dd469e1ceb92f73e8f8c2d81502e10defebc9c46` |

File sizes: `arms_holdout_deploy_per_image.npz` 655.0 KiB, `arms_holdout_deploy_arms.csv` 141.8 KiB, `confirm_resnet50_per_image.npz` 650.7 KiB, `confirm_resnet50_arms.csv` 142.3 KiB, `arms_holdout_c100_per_image.npz` 1003.5 KiB, `arms_holdout_c100_arms.csv` 143.2 KiB, `aetta_src_750_rounds.csv` 347.9 KiB, `aetta_tgt_750_paired_rounds.csv` 348.1 KiB, `aetta_v3_750_rounds.csv` 348.0 KiB, `aetta_c100_750_rounds.csv` 349.7 KiB.
