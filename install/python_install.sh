mkdir -p ~/tmp/inst
cd ~/tmp/inst
wget https://www.python.org/ftp/python/3.6.6/Python-3.6.6.tar.xz
tar xf Python-3.6.6.tar.xz && cd Python-3.6.6
./configure
sudo make -j 15 && sudo make install
python3 -m venv ~/venv
source ~/venv/bin/activate
pip install -r requements.txt