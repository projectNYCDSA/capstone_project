


airdata <- read.csv('test.txt',sep = '|')

class(airdata)

colnames(airdata)
summary(airdata)
sapply(airdata, sd)

unique(airdata$id_visitor)

