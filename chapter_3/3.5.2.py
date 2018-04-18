import numpy as np
import matplotlib.pyplot as plt
import argparse

def create_dataset(N, function=np.sin):
    # train_data
    train_x = np.random.uniform(0, 7, N)
    train_y = function(train_x)
    # ground_truth
    gt_x = np.linspace(0, 7)
    gt_y = function(gt_x)

    return [train_x, train_y], [gt_x, gt_y]

def plotting(ground_truth, train_data, prediction):
    plt.plot(train_data[0],train_data[1], "o")
    plt.plot(ground_truth[0], ground_truth[1], color='r')
    plt.plot(ground_truth[0], prediction[0], color='b')
    plt.plot(ground_truth[0], prediction[1], linestyle='--', color='c')
    plt.plot(ground_truth[0], prediction[2], linestyle='--', color='c')
    
    plt.xlim([-0.5, 7])
    plt.ylim([-3, 3])

    plt.show()


class BaysianLinearRegression(object):
    def __init__(self, M, s_lam):
        self.M = M
        self.s_lam = s_lam
        self.prior_m = np.zeros(M)
        self.prior_l_lam = np.eye(M,M)
    
    def mapping(self, x):
        x = x.reshape(1, -1)
        x_vec = np.concatenate([
            np.power(x, i) for i in range(self.M)],
            axis=0)
        return x_vec

    def calcurate_posterior(self, tx, ty):
        tx = tx.T
        ynxn = 0
        xnxn = 0
        for x, y in zip(tx, ty):
            x = x.reshape(1, -1)
            ynxn += y * x
            xnxn += np.dot(x.T, x)
        post_l_lam = self.s_lam * xnxn + self.prior_l_lam
        inv_post_l_lam = np.linalg.inv(post_l_lam)
        post_m = self.s_lam * ynxn + np.dot(self.prior_l_lam, self.prior_m)
        post_m = np.dot(inv_post_l_lam, post_m.T)

        self.prior_m = post_m
        self.prior_l_lam = post_l_lam
        
        return post_m, post_l_lam
    
    def calcurate_predictive(self, xs, post_m=None, post_l_lam=None):
        if post_m is None and post_l_lam is None:
            post_m = self.prior_m
            post_l_lam = self.prior_l_lam

        inv_post_l_lam = np.linalg.inv(post_l_lam)

        post_s_lam = 1 / self.s_lam + np.dot(np.dot(xs.T, inv_post_l_lam), xs)
        post_s_lam = np.diag(post_s_lam).reshape(-1, 1)

        output_y_u = np.dot(xs.T, post_m)
        output_y_u_plam = output_y_u + np.sqrt(post_s_lam)
        output_y_u_mlam = output_y_u - np.sqrt(post_s_lam)

        return output_y_u, output_y_u_plam, output_y_u_mlam

def main(args):
    M = args.M
    N = args.N
    s_lam = args.s_lam

    train_data, ground_truth = create_dataset(N)

    model = BaysianLinearRegression(args.M, args.s_lam)
    train_x_vec = model.mapping(train_data[0])
    gt_x_vec = model.mapping(ground_truth[0])
    post_m, post_l_lam = model.calcurate_posterior(train_x_vec, train_data[1])
    prediction = model.calcurate_predictive(gt_x_vec)

    plotting(ground_truth, train_data, prediction)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='linear regression')
    parser.add_argument('--M', type=int, default=4,
                        help='input dimention')
    parser.add_argument('--N', type=int, default=10,
                        help='number of train data')
    parser.add_argument('--s_lam', type=float, default=10.0,
                        help='accracy parameter')
    args = parser.parse_args()

    main(args)