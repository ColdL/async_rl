import tensorflow as tf
import numpy as np
import gym
from gym import wrappers
from model import QFuncModel
from utils import *
from config import *

env = gym.make(args.game)
args.actions = len(keymap[args.game])
model_target = QFuncModel(args)
saver = tf.train.Saver()
ckpt = tf.train.get_checkpoint_state(args.save_dir)
average = 0.0
with tf.Session() as sess:
    saver.restore(sess, ckpt.model_checkpoint_path)
    env = wrappers.Monitor(env, 'play', force=True)
    for episode in range(args.num_play_episode):
        x_t = env.reset()
        x_t = rgb2gray(resize(x_t))
        s_t = np.stack([x_t for _ in range(args.frames)], axis=2)
        total_reward = 0
        action_index = 0
        t = 0
        while True:
            #env.render()
            a_t = np.zeros([args.actions])
            readout_t = sess.run(model_target.readout, feed_dict={model_target.s: [s_t]})
            action_index = np.argmax(readout_t)
            print keymap[args.game][action_index],
            a_t[action_index] = 1
            x_t_next, r_t, terminal, info = env.step(keymap[args.game][action_index])
            total_reward += r_t
            if terminal:
                break
            else:
                x_t_next = rgb2gray(resize(x_t_next))
                s_t = np.append(x_t_next[:, :, np.newaxis], s_t[:, :, 0:3], axis=2)
            t += 1
        average += total_reward
        print "episode %d: score %d, current average: %f" % (episode, total_reward, average / (episode + 1))


