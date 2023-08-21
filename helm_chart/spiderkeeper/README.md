# 部署命令

helm install -f values.yaml --create-namespace --namespace spiderkeeper spiderkeeper .

helm upgrade -f values.yaml --namespace spiderkeeper spiderkeeper .

helm uninstall --namespace spiderkeeper spiderkeeper
