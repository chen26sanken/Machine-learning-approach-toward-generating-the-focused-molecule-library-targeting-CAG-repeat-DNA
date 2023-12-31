import os
import matplotlib.pyplot as plt
import random
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.model_selection import StratifiedKFold
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import *
from sklearn.model_selection import train_test_split
from imblearn.over_sampling import SMOTE
from collections import Counter
import shap
from imblearn.over_sampling import RandomOverSampler, SMOTENC
import categorical_index
from sklearn import model_selection
import tqdm


# Function to check if a value is a number
def isnumber(x):
    try:
        float(x)
        return True
    except:
        return False


# sum all elements except the top 5 and bottom 5 in an array
def sum_noHL(arr):
    return sum(sorted(arr)[5:-5])


# RF parameters
my_max_depth = 7
num_tree = 300


the_infile = 'dataset/Dragon_2000cpds.csv'
# the_infile = 'dataset/Dragon_2000cpds_woTop10.csv'
# the_infile = 'few_top_features.csv'
the_outfile = "output_temp"

# the number of top features to save, number of cross-validation splits, random seed,
# number of non-hits dropped from training data, and the number of times to repeat this process
top_k = 20  # number of feature show in the plot
cv_splits = 3
random_seed = 50000
dropped_nonhit = 1450  # adjust the data balance
repeat_times = 100  # the repeated experiment for classification

# store categorical index for oversampling
categorical = categorical_index.categorical_index_fc()
rsp = SMOTENC(random_state=6000, categorical_features=categorical)

tree_index = 3  # Should be within [0, n_estimators-1]
main_info = "0.2tst_rt_" + "dep" + str(my_max_depth) + \
            "tree" + str(num_tree) + "seed" + str(random_seed) + \
            "drop_nh" + str(dropped_nonhit)


out_feature_rank = the_outfile + "/feature_rank_" + main_info + ".txt"
saved_trees = "trees_" + str(tree_index) + main_info
os.makedirs(the_outfile + "/", exist_ok=True)


if __name__ == '__main__':
    frame = pd.read_csv(the_infile, low_memory=False)
    frame.head()

    # Remove the first column (label identifier) from the data
    data = frame.iloc[:, 1:]
    header = list(data.columns)  # store column names for input of SHAP explainer
    data = data[data.applymap(isnumber)].to_numpy().astype(float)  # set non-numeric values to 0
    data[np.isnan(data)] = 0
    # print("data", data.shape)
    data_df = pd.DataFrame(data, columns=header)  # input of SHAP explainer

    # Set labels for data
    two_class_separation = True
    labels = frame.iloc[:, [0]].to_numpy().flatten()  # grab the first column: "binder xxx" or "non binder xxx"
    numeric_labels = np.zeros(labels.shape)  # give all data a "0" label

    nonhit_index = 104
    if two_class_separation:
        numeric_labels[nonhit_index:] = 1  # 0
    else:
        numeric_labels[34:67] = 1  # hit_slow labeled as 0, hit_fast as 1
        numeric_labels[nonhit_index:] = 2  # 2 for non-hit

    # train test data splitting
    np.random.seed(random_seed)  # fixing the randomness
    X_train, X_test, y_train, y_test = train_test_split(data_df, numeric_labels, test_size=0.2)

    n = 0
    index_nonhit_trn = []
    for i in y_train:
        n += 1
        if i == 1:
            index_nonhit_trn.append(n - 1)
    index_nonhit_trn = index_nonhit_trn
    print("nonhit counts in training: ", len(index_nonhit_trn), "\n")
    X_train_reset_id = X_train.reset_index()
    y_train_ = y_train

    # initializing empty lists with specific names for later use
    rcd_result = []
    rcd_f1 = []
    rcd_recall = []
    rcd_precision = []
    rcd_X_test = []
    rcd_y_test = []
    rcd_y_pred = []
    importance_gini_all = []
    importance_shap_all = []

    random.seed(random_seed)  # seeds for reproducibility
    for random_i in random.sample(range(0, 100000), repeat_times):
        random.seed(random_i)
        index_nonhit_trn_removed = sorted(random.sample(index_nonhit_trn, dropped_nonhit))

        X_train_2 = X_train_reset_id.drop(index_nonhit_trn_removed)  # remove nonhits by index
        X_train = X_train_2.set_index(["index"])
        y_train = np.delete(y_train_, index_nonhit_trn_removed, 0)

        # # resampling (oversampling)
        # print('Orl %s' % Counter(y_train))
        # X_train, y_train = rsp.fit_resample(X_train, y_train)
        # print('Respl %s' % Counter(y_train))

        my_max_depth = my_max_depth
        # X_train = X_train.values.tolist()  # adjust the datatype for xgboost
        # clf = XGBClassifier(max_depth=my_max_depth, random_state=0, n_estimators=num_tree) 
        # commented out specifice lines when use xgb classifier to skip datatype errors 
        
        clf = RandomForestClassifier(max_depth=my_max_depth, random_state=0, n_estimators=num_tree)
        clf.fit(X_train, y_train)

        # Visualization
        feature_names = pd.read_csv(the_infile, nrows=1, low_memory=False).columns
        feature_names = list(feature_names[1:])
        for i, name in enumerate(feature_names):
            name = name + '[%d]' % i
            feature_names[i] = name
        if two_class_separation:
            class_names = ['hit', 'non-hit']
        else:
            class_names = ['hit_s', 'hit_f', 'non-hit']

        # cm in training dataset
        y_pred_train = clf.predict(X_train)
        cm_train = confusion_matrix(y_train, y_pred_train, labels=[0, 1])
        print("confusion matrix (training)\n", cm_train)

        # evaluation scores on testing dataset
        y_pred = clf.predict(X_test)
        cm = confusion_matrix(y_test, y_pred, labels=[0, 1])

        # f1 scores
        f1 = f1_score(y_test, y_pred, average=None)
        rcd_f1.append(f1[0])  # f1 for hits
        rounded_arr_f1 = np.round(rcd_f1, 2)  # round the values of the ndarray to 2 decimal places

        # recall scores
        recall = recall_score(y_test, y_pred, average=None)
        rcd_recall.append(recall[0])  # recall for hits
        rounded_arr_recall = np.round(rcd_recall, 2)  # round the values of the ndarray to 2 decimal places
        print("\n----- new result added ------------")

        # precision scores (focused molecule library index)
        precision = precision_score(y_test, y_pred, average=None)
        rcd_precision.append(precision[0])  # precision for hits
        rounded_arr_prec = np.round(rcd_precision, 2)  # round the values of the ndarray to 2 decimal places

        # compute the importance each experiment (gini index)
        importance_gini = clf.feature_importances_  # compute the feature importance
        importance_gini_all.append(importance_gini)  # append

        # compute the importance each experiment (shap value) (comment out line 178-183 when use xgboost)
        explainer = shap.TreeExplainer(clf, feature_perturbation='interventional')
        shap_values = explainer.shap_values(data_df)
        col_abs_sum = np.sum(np.abs(shap_values[0]), axis=0)
        mean = col_abs_sum / shap_values[0].shape[0]  # this mean is the
        importance_shap_all.append(mean)

        # print("Column absolute sum: ", col_abs_sum)
        # print("Mean: ", mean)
        # print(mean.shape)
        # breakpoint()

        # calculate avg of recall without top and bottom 5% value
        sorted_array = np.sort(rounded_arr_recall)
        trimmed_array = sorted_array[5:-5]
        if len(trimmed_array) > 0:  # division by zero cause error
            avg_recall = sum(trimmed_array) / len(trimmed_array)
        else:
            avg_recall = " -- "

        # calculate avg of F1 without top and bottom 5% value
        sorted_array = np.sort(rounded_arr_f1)
        trimmed_array = sorted_array[5:-5]
        if len(trimmed_array) > 0:  # division by zero cause error
            avg_f1 = sum(trimmed_array) / len(trimmed_array)
        else:
            avg_f1 = " -- "

        sorted_array = np.sort(rounded_arr_prec)
        trimmed_array = sorted_array[5:-5]
        if len(trimmed_array) > 0:  # division by zero cause error
            avg_prec = sum(trimmed_array) / len(trimmed_array)
        else:
            avg_prec = " -- "

        # append list during each training for confusion matrix
        rcd_X_test.append(X_test)
        rcd_y_test.append(y_test)
        rcd_y_pred.append(y_pred)

        prec_index = 0
        max_prec_index = 0

        # # search with the highest precision
        max_prec = rcd_precision[0]  # assume the first number is the largest
        for i in rcd_precision:
            if i > max_prec:  # if a number is larger than the current max
                max_prec = i  # set it as the new max
                max_prec_index = prec_index
                print("!!!!!! FIND a higher precision: ", max_prec,
                      "id:", max_prec_index)
                # plot & save cm
                cm = confusion_matrix(rcd_y_test[max_prec_index], rcd_y_pred[max_prec_index])
                print("confusion matrix_test\n", cm)
                disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=class_names)
                disp.plot(colorbar=False, cmap="Blues")
                disp.ax_.set_title("testing", fontsize=25)
                # set font size of text elements in plot
                for i in range(disp.confusion_matrix.shape[0]):
                    for j in range(disp.confusion_matrix.shape[1]):
                        disp.text_[i, j].set_fontsize(35)

                # remove x and y ticks
                disp.ax_.tick_params(bottom=False, left=False, labelsize=25)
                disp.ax_.set_yticklabels(class_names, rotation=90, verticalalignment='center')

                # disp.ax_.set_xlabel('Predictive Label', fontsize=20)
                # disp.ax_.set_ylabel('True Label', fontsize=20)
                disp.ax_.set_xlabel('')
                disp.ax_.set_ylabel('')
                disp.ax_.set_frame_on(False)
                plt.tight_layout()
                # save the best cm result
                plt.savefig(the_outfile + '/Hprec_' + main_info + '.png')
                # plt.show()
                plt.close()

                # plotting feature importance
                importance = clf.feature_importances_  # compute the feature importance
                indices = np.argsort(importance)[::-1]  # Sort them in descending order

                # Rearrange feature names let they match the sorted feature importance
                names = [feature_names[i] for i in indices]
                names = np.array(names)

                new_indices = indices[:top_k]
                with open(out_feature_rank, 'w') as fd:  # write the feature ranking to txt file;
                    # "w": an existing file with the same name will be erased
                    fd.write("entry" + "," + "feature_name" + "," + "feature_index_check" +
                             "," + "feature_importance_value" + "1000*feature_importance_value" + "\n")
                    for f in range(top_k):  # loop over the top k features
                        fd.write(str(f + 1) + "," + names[f] + "," + str(new_indices[f]) +
                                 "," + str(importance[new_indices[f]]) + "," + str(
                            1000 * importance[new_indices[f]]) + "\n")

                # plot the result in histogram
                plt.figure(figsize=(8, 12), constrained_layout=True, dpi=300)
                flipped_importance = np.flip(importance[new_indices], axis=None)  # from horizontal to vertical
                plt.barh(range(top_k), flipped_importance,
                         color="cornflowerblue", align="center")
                flipped_name = np.flip(names[:top_k], axis=None)
                plt.yticks(range(top_k), flipped_name, fontsize=15)
                plt.xticks(fontsize=13)
                plt.gca().spines['top'].set_visible(False)
                plt.gca().spines['right'].set_visible(False)
                plt.savefig(the_outfile + '/' + 'feature_rank_' + main_info + '.png')
                plt.close()

                # SHAP implementation ------------------------------- (comment out line 286-298 when use xgboost)
                X = data_df
                explainer = shap.TreeExplainer(clf, feature_perturbation='interventional')
                shap_values = explainer.shap_values(X)
                # important feature ranking from shap
                shap.summary_plot(shap_values[0], plot_type="bar", class_names=class_names, feature_names=X.columns,
                                  show=False, max_display=20)
                plt.savefig(the_outfile + "/shap_FtrImp" + main_info + '.jpg', bbox_inches='tight', dpi=300)
                plt.close()

                shap.summary_plot(shap_values[1], X.values, feature_names=X.columns, show=False)
                plt.savefig(the_outfile + "/Beeswarm_" + main_info + '.jpg', bbox_inches='tight', dpi=300)
                plt.close()

            else:
                print("-")
            prec_index += 1

        # find the max value in recall & use the index to plot cm
        max_recall = max(rounded_arr_recall)
        max_recall_index = np.argmax(rounded_arr_recall)
        print("the index", max_recall_index)

        # find the max value in f1
        max_f1 = max(rounded_arr_f1)

        # find the max value in precision & use the index to plot cm
        max_prec = max(rounded_arr_prec)
        max_prec_index = np.argmax(rounded_arr_prec)
        print("the prec index", max_prec_index)

        # plot & save cm
        cm = confusion_matrix(rcd_y_test[max_recall_index], rcd_y_pred[max_recall_index])
        print("confusion matrix_test\n", cm)
        disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=class_names)
        disp.plot(colorbar=False, cmap="Blues")
        disp.ax_.set_title("testing", fontsize=25)
        # set font size of text elements in plot
        for i in range(disp.confusion_matrix.shape[0]):
            for j in range(disp.confusion_matrix.shape[1]):
                disp.text_[i, j].set_fontsize(35)

        # remove x and y ticks
        disp.ax_.tick_params(bottom=False, left=False, labelsize=25)
        disp.ax_.set_yticklabels(class_names, rotation=90, verticalalignment='center')

        # disp.ax_.set_xlabel('Predictive Label', fontsize=20)
        # disp.ax_.set_ylabel('True Label', fontsize=20)
        disp.ax_.set_xlabel('')
        disp.ax_.set_ylabel('')
        disp.ax_.set_frame_on(False)
        plt.tight_layout()
        # save the best cm result
        plt.savefig(the_outfile + '/Hrecall_' + main_info + '.png')
        # plt.show()
        plt.close()

        # save the result
        with open(the_outfile + "/scores" + main_info + ".txt", 'w') as fd:
            fd.write("scores  " + str(len(rounded_arr_recall)) + " record"

                     # recall
                     + "\n\nrecall" + str(rounded_arr_recall)
                     + "\nmax:" + str(max_recall)
                     + "\navg:" + str(avg_recall)

                     # f1
                     + "\n\nf1" + str(rounded_arr_f1)
                     + "\nmax:" + str(max_f1)
                     + "\navg:" + str(avg_f1)

                     # precision
                     + "\n\nprecision" + str(rounded_arr_prec)
                     + "\nmax:" + str(max_prec)
                     + "\navg:" + str(avg_prec))


# ROC with 3-fold cross validation -------------------------------
    X = np.concatenate((X_train, X_test), axis=0)
    y = np.concatenate((y_train, y_test), axis=0)
    print("len(X)", len(X), "len(y)", len(y))

    # Run classifier with cross-validation and plot ROC curves
    cv = StratifiedKFold(n_splits=cv_splits)
    clf_cv = RandomForestClassifier(max_depth=my_max_depth, random_state=0, n_estimators=num_tree)
    # clf would be used in the last shap part, clf_cv only for cross validation

    tprs = []
    aucs = []
    mean_fpr = np.linspace(0, 1, 100)

    fig, ax = plt.subplots(figsize=(12, 11))
    ax.set(facecolor="white")
    ax.spines['right'].set_color('black')
    ax.spines['bottom'].set_color('black')
    ax.spines['top'].set_color('black')
    ax.spines['left'].set_color('black')
    ax.tick_params(labelsize=40)
    ax.set_ylabel("True Positive rate", fontsize=25)
    ax.set_xlabel("False Positive rate", fontsize=25)

    for i, (train, test) in enumerate(cv.split(X, y)):
        clf_cv.fit(X[train], y[train])
        viz = RocCurveDisplay.from_estimator(
            clf_cv,
            X[test],
            y[test],
            name="ROC fold {}".format(i + 1),
            alpha=0.3,
            lw=1,
            ax=ax,
            pos_label=0
        )
        interp_tpr = np.interp(mean_fpr, viz.fpr, viz.tpr)
        interp_tpr[0] = 0.0
        tprs.append(interp_tpr)
        aucs.append(viz.roc_auc)

    ax.plot([0, 1], [0, 1], linestyle="--", lw=2, color="r", label="Chance", alpha=0.8)
    # ax.tick_params(labelsize=25)

    mean_tpr = np.mean(tprs, axis=0)
    mean_tpr[-1] = 1.0
    mean_auc = auc(mean_fpr, mean_tpr)
    std_auc = np.std(aucs)
    ax.plot(
        mean_fpr,
        mean_tpr,
        color="b",
        label=r"Mean ROC (AUC = %0.2f $\pm$ %0.2f)" % (mean_auc, std_auc),
        lw=2,
        alpha=0.8,
    )

    std_tpr = np.std(tprs, axis=0)
    tprs_upper = np.minimum(mean_tpr + std_tpr, 1)
    tprs_lower = np.maximum(mean_tpr - std_tpr, 0)
    ax.tick_params(labelsize=30)
    ax.fill_between(
        mean_fpr,
        tprs_lower,
        tprs_upper,
        color="grey",
        alpha=0.2,
        label=r"$\pm$ 1 std. dev.",
    )

    ax.set(
        xlim=[-0.05, 1.05],
        ylim=[-0.05, 1.05],
        # title="Receiver operating characteristic",
    )
    # ax.set_title("Receiver operating characteristic", fontsize=22)
    ax.legend(loc="lower right", fontsize=21)
    plt.savefig(the_outfile + "/AUC_cv_" + main_info + "_cv" + str(cv_splits) + '.png')
    plt.show()
    plt.close(fig)

    # calculate and save the sum of feature importance for gini
    # gini sum
    # calculate sum along columns
    sums = np.sum(importance_gini_all, axis=0)
    sums_list = list(zip(feature_names, sums))  # create a list of tuples with (feature name, sum) pairs
    sorted_sums = sorted(sums_list, key=lambda x: x[1], reverse=True)  # sort in descending order
    # # print the sorted results
    # for feature, s in sorted_sums:
    #     print(f"Sum of {feature}: {s}")

    # save the sorted results to a file
    with open('all_sorted_sums_gini.txt', 'w') as f:
        for feature, s in sorted_sums:
            f.write(f"Sum of {feature}: {s}\n")

    # shap sum (comment out line 459-467 when use xgboost)
    sums = np.sum(importance_shap_all, axis=0)
    sums_list = list(zip(feature_names, sums))
    sorted_sums = sorted(sums_list, key=lambda x: x[1], reverse=True)

    # save the sorted results to a file
    with open('all_sorted_sums_shap.txt', 'w') as f:
        for feature, s in sorted_sums:
            f.write(f"Sum of {feature}: {s}\n")


