Prices = read.csv("train.csv")

library(tidyverse) # metapackage of all tidyverse packages
library(glmnet) #ridge and LASSO regression package
library(pls) #partial least squares regression package

Prices = subset(Prices, select = -Id)

#sort predictors into numeric and categorical
npred = ncol(Prices) - 1
num_pred_i = c(3,4,17,18,19,20,26,34,36,37,38,43,44,45,46,59,62,66,67,68,69,70,71,75,77)
cat_pred_i = 1:npred
cat_pred_i = cat_pred_i[-num_pred_i]

#replace NA entries with more meaningful values
nacols = which(colSums(is.na(Prices)) > 0)
for (i in nacols) {
  if (class(Prices[,i]) == "character") {
    Prices[,i] = replace_na(Prices[,i],"None")
  }
  else {
    Prices[,i] = replace_na(Prices[,i],0)
  }
}

#scale numeric predictors and turn categorical predictors into factors
Prices[,num_pred_i] = scale(Prices[,num_pred_i])
for (i in cat_pred_i) {
  Prices[,i] = factor(Prices[,i])
}

#create objects for LASSO regression
SalePrice = Prices$SalePrice
xmat = data.matrix(Prices[,-80])

#use cross-validation to determine the optimal value of lambda
lassoCV = cv.glmnet(xmat, SalePrice, alpha = 1)

#create LASSO model with optimal lambda
lassoModel = glmnet(x = xmat, y = SalePrice, family = "gaussian", alpha = 1, lambda = lassoCV$lambda.min)

#create partial least squares regression (PLSR) model
plsrModel = plsr(SalePrice ~ ., data = Prices, validation = "CV")

#read in test data
test = read.csv("test.csv")
testId = test$Id
test = subset(test, select = -Id)

#replace NA entries with more meaningful values
nacols = which(colSums(is.na(test)) > 0)
for (i in nacols) {
  if (class(test[,i]) == "character") {
    test[,i] = replace_na(test[,i],"None")
  }
  else {
    test[,i] = replace_na(test[,i],0)
  }
}

#scale numeric predictors and turn categorical predictors into factors
test[,num_pred_i] = scale(test[,num_pred_i])
for (i in cat_pred_i) {
  test[,i] = factor(test[,i])
}
test = data.matrix(test)

#make predictions using LASSO model
predsLASSO = predict(lassoModel, newx = test, type = "response")

#make predictions using PLSR model
predsPLSR = predict(plsrModel, newx = test, type = "response", ncomp = 118)

preds = cbind(testId,predsPLSR[-1460])
colnames(preds) = c("Id", "SalePrice")

write.csv(preds, "submission.csv", row.names = F)

