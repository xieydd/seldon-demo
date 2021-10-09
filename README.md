## seldon-demo
Demo for seldon core

### Install Seldon 
#### Install Seldon Normal
```
git clone https://github.com/SeldonIO/seldon-core.git /tmp/seldon-core
kubectl create namespace seldon-system
helm install seldon-core /tmp/seldon-core/helm-charts/seldon-core-operator \
    --set usageMetrics.enabled=true \
    --namespace seldon-system
```

#### Install Seldon Istio

```
$ kubectl create namespace istio-system
```
Using TKE Mesh create service mesh. notice set name `seldon-gateway` in `istio-system`, create ingress gateway watch default namespace application. Then create Gateway `seldon-gateway` in default namespace and set port is 8080

```
git clone https://github.com/SeldonIO/seldon-core.git /tmp/seldon-core
kubectl create namespace seldon-system
helm install seldon-core /tmp/seldon-core/helm-charts/seldon-core-operator \
    --set usageMetrics.enabled=true \
    --namespace seldon-system \
    --set istio.enabled=true
```

### Simple Demo
1. Create fashion mnist SeldonDeployment
```
$ kubectl apply -f normal/fashion_mnist.yaml
```

2. If you don`t have the model, you can train yourself
```
$ docker run -it --net host --name test -v ./:/tmp ccr.ccs.tencentyun.com/kubeflow-oteam/seldon-gpt2-demo:20210813-xieydd /bin/bash
$ git clone https://github.com/abhijeet3922/tf-fashionMNIST.git
$ cd tf-fashionMNIST && python DeepFashion.py
```

3. Inference
```
$ kubectl port-forward $(kubectl get pods -l istio=ingressgateway -n istio-system -o jsonpath='{.items[0].metadata.name}') -n istio-system 8004:8080
export SELDON_URL=localhost:8004
$ cd normal && python fashion_mnist_inference.py
```
 You can find the result of the inference and the image of your input data.

### Canary Demo
- Istio Canary demo: https://docs.seldon.io/projects/seldon-core/en/v0.3.1/examples/istio_canary.html
- Multi-model demo: https://docs.seldon.io/projects/seldon-core/en/latest/examples/protocol_examples.html?highlight=half_plus_two#Tensorflow-Protocol-Multi-Model

1. Create canary multi model SeldonDeployment
```
$kubectl apply -f canary/multi-model-canary-tfserving.yaml
```

2. Inference
```
$ kubectl port-forward $(kubectl get pods -l istio=ingressgateway -n istio-system -o jsonpath='{.items[0].metadata.name}') -n istio-system 8004:8080
export SELDON_URL=localhost:8004
$ python canary/multi_model_canary_inference.py
```

3. Monitor
You can check TKE Service Mesh Montoring for the inference service, we can check the request is following a three-to-one distribution.

### GPU Demo
- GPT2 demo : https://docs.seldon.io/projects/seldon-core/en/stable/examples/triton_gpt2_example.html

1. Prepare model
```
$ docker run -it --net host --name test -v ./:/tmp ccr.ccs.tencentyun.com/kubeflow-oteam/seldon-gpt2-demo:20210813-xieydd /bin/bash
$ python export_huggingface_model.py
$ python -m tf2onnx.convert --saved-model ./tfgpt2model/saved_model/1 --opset 11  --output model.onnx
```
2. Upload model to cos
Detail can be found in https://cloud.tencent.com/document/product/436/10976

3. Deploy COS pvc(TKE need enable cos csi addon)
```
$ kubectl apply -f cos/secret.yaml
$ kubectl apply -f cos/pv.yaml
$ kubectl apply -f cos/pvc.yaml
```

4. Deploy triton gpt2 SeldonDeployment
```
$ kubectl apply -f gpu/triton_gpt2.yaml
```

5. Inference
In test container
```
$ kubectl port-forward $(kubectl get pods -l istio=ingressgateway -n istio-system -o jsonpath='{.items[0].metadata.name}') -n istio-system 8004:8080
export SELDON_URL=localhost:8004
$ python inference.py
```

6. Load Performance Test
```
$ wget https://github.com/tsenart/vegeta/releases/download/v12.8.3/vegeta-12.8.3-linux-amd64.tar.gz
$ tar -zxvf vegeta-12.8.3-linux-amd64.tar.gz
$ chmod +x vegeta
$ python vegeta_target_json.py
$ vegeta attack -targets=vegeta_target.json -rate=1 -duration=60s -format=json | vegeta report -type=text
```

### COS Configuration

In cos dir, we can create secret、pv and pvc via cos csi in tke. Detail can be found in https://cloud.tencent.com/document/product/457/44232.

Seldon core adapter:
- 微保
- 伴鱼 https://tech.ipalfish.com/blog/2021/08/02/deploy_lightgbm_models_with_seldoncore/