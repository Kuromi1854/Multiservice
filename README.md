pour pouvoir utiliser ce code il faut d'abord telecharger quelques extensions python
sur les distros linux base sur arch, ce sont les commandes suivantes:
sudo pacman -S python3 pip3
ensuite
pip install streamlit pendas uvicorn
Sur windows meme chose mais dans le powershell
apres pour que le programme marche sur votre navigateur
cd "enplacement du repertoire"
streamlit run projet_final.py
si cela ne marche pas en general sur windows essayez la commande suivante
python -m streamlit run projet_final.py
