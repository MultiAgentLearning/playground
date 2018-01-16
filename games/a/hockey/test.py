import tensorflow as tf

import configs
import utility


if __name__=="__main__":
    FLAGS = tf.app.flags.FLAGS
    tf.app.flags.DEFINE_string('config', 'test1v1', 'Configuration to execute.')
    config = utility.AttrDict(getattr(configs, FLAGS.config)())
    env = config.env(num_agents_per_team=config.num_agents_per_team, gas_bins=config.gas_bins,
                     brake_bins=config.brake_bins, steer_bins=config.steer_bins, )

    while True:
        print("Starting a new environment!")
        obs = env.reset()
        total_reward = 0.0
        steps = 0
        done = False
        while not done:
            print("Steps: %d" % steps)
            steps += 1
            env.render()
            actions = utility.random_actions(env.action_space)
            obs, reward, done, info = env.step(actions)
    env.close()
