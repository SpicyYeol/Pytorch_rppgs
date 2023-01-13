import os
import torch
from matplotlib import pyplot as plt
from tqdm import tqdm
import json
import wandb
import vid2bp.preprocessing.utils.signal_utils as su
import vid2bp.postprocessing.post_signal_utils as psu
import numpy as np
import vid2bp.utils.train_utils as tu
from vid2bp.nets.loss.loss import SelfScaler


def validation(model, dataset, loss_list, epoch, scaler=True):
    model.eval()
    scale_loss = SelfScaler().to('cuda:0')

    avg_cost_list = []
    dy_avg_cost_list = []
    ddy_avg_cost_list = []
    for _ in range(len(loss_list)):
        avg_cost_list.append(0)
        dy_avg_cost_list.append(0)
        ddy_avg_cost_list.append(0)

    with tqdm(dataset, desc='Validation{}'.format(str(epoch)), total=len(dataset), leave=True) as valid_epoch:
        with torch.no_grad():
            for idx, (X_val, dx, ddx, Y_val, dy, ddy, d, s) in enumerate(valid_epoch):
                hypothesis, dy_hypothesis, ddy_hypothesis, scaled_ple = model(X_val, dx, ddx, scaler=scaler)
                avg_cost_list, _ = tu.calc_losses(avg_cost_list, loss_list,
                                                  hypothesis, Y_val, idx + 1)
                dy_avg_cost_list, _ = tu.calc_losses(dy_avg_cost_list, loss_list,
                                                     dy_hypothesis, dy, idx + 1)
                ddy_avg_cost_list, _ = tu.calc_losses(ddy_avg_cost_list, loss_list,
                                                      ddy_hypothesis, ddy, idx + 1)

                ple_cost = scale_loss(scaled_ple, X_val)
                total_cost = torch.sum(torch.tensor(avg_cost_list)) + torch.sum(
                    torch.tensor(dy_avg_cost_list)) + torch.sum(torch.tensor(ddy_avg_cost_list)) + \
                             ple_cost

                postfix_dict = {}
                for i in range(len(loss_list)):
                    postfix_dict[(str(loss_list[i]))[:-2]] = (round(avg_cost_list[i], 3))
                postfix_dict['scale_variance'] = round(ple_cost.__float__(), 3)
                valid_epoch.set_postfix(losses=postfix_dict, tot=total_cost)
            # wandb.init(project="VBPNet", entity="paperchae")
            # wandb.log({"Valid Loss": total_cost}, step=epoch)
            # wandb.log({"Valid Loss": valid_avg_cost,
            #            'Valid Pearson Loss': neg_cost,
            #            'STFT Loss': stft_cost}, step=epoch)
        return total_cost.__float__()
