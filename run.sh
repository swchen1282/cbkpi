sudo docker stop api
sudo docker rm api
sudo docker run -d --name api -p 5001:5000 fast-api
