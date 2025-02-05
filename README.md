
---

# 🚀 Assistant Français IA - Interaction vocale avec un LLM en local

**Assistant Français IA** est un agent vocal interactif qui utilise un **modèle de LLM local** (via **Ollama**) pour comprendre et répondre aux demandes des utilisateurs.  
L'agent écoute la voix, reconnaît l'intention, génère une réponse, valide la réponse et peut exécuter des actions comme envoyer un email ou lancer une visioconférence.

---

## **📌 Fonctionnalités**
✅ **Reconnaissance vocale** (écoute et conversion en texte)  
✅ **Synthèse vocale** (réponse parlée)  
✅ **Interaction avec un LLM local** (via **Ollama**)  
✅ **Détection d'intention** (ex: envoyer un email, lancer une visio)  
✅ **Exécution de commandes** (ex: ouvrir un programme, afficher une image)  
✅ **Vérification de la réponse générée** avant de parler  

---

## **⚡ Installation**

### **1️⃣ Pré-requis**
Avant de commencer, assure-toi d’avoir les éléments suivants installés :

🔹 **Python 3.11+**  
🔹 **pip et virtualenv**  
🔹 **Ollama** (Serveur de LLM local)  

### **2️⃣ Cloner le projet**
```bash
git clone https://github.com/ton-profil/assistant-francais.git
cd assistant-francais
```

### **3️⃣ Créer un environnement virtuel**
```bash
python -m venv .venv
source .venv/bin/activate  # Mac/Linux
# ou
.venv\Scripts\activate  # Windows
```

### **4️⃣ Installer les dépendances**
```bash
pip install -r requirements.txt
```

### **5️⃣ Installer Ollama**
Si Ollama n'est pas encore installé :
```bash
brew install ollama  # macOS avec Homebrew
```
ou
```bash
curl https://ollama.ai/install.sh | sh  # Linux/macOS
```

### **6️⃣ Télécharger le modèle LLM**
```bash
ollama pull tinyllama
```

---

## **🚀 Utilisation**
### **1️⃣ Lancer Ollama en arrière-plan**
```bash
ollama serve
```

### **2️⃣ Démarrer l’assistant**
```bash
python backend/app/assistant_francais.py
```

### **3️⃣ Fonctionnement**
📢 **Parle à ton assistant !** Il écoute, analyse et répond.  

**Exemples de commandes vocales :**  
🗣️ *"Je voudrais écrire un email"* → **L’agent ouvre l’email**  
🗣️ *"Je veux démarrer une visioconférence"* → **L’agent démarre la visio**  
🗣️ *"Affiche mes photos"* → **L’agent ouvre le dossier photo**  
🗣️ *"Je veux imprimer un document"* → **L’agent lance l’impression**  

Tu peux arrêter l’agent en disant *"Non, c’est bon, merci."*  

---

## **🛠️ Développement et Personnalisation**
### **Modifier les actions exécutées**
Les actions sont définies dans `execute_command(intent)`.  
Elles sont liées aux modules :
- `services/email.py` (Email)
- `services/visio.py` (Visioconférence)
- `services/photo.py` (Photos)
- `services/printing.py` (Impression)

Ajoute d’autres actions selon tes besoins.

---

## **🔍 Dépannage**
### **Problème : Ollama ne répond pas**
❌ **Erreur** : `model "tinyllama" not found`  
✔ **Solution** :  
1. Vérifie que le modèle est installé :  
   ```bash
   ollama list
   ```
2. S'il n'apparaît pas, installe-le à nouveau :  
   ```bash
   ollama pull tinyllama
   ```

### **Problème : Pas de réponse vocale**
❌ **Erreur** : L’agent ne parle pas  
✔ **Solution** : Installe ou réinstalle `pyttsx3` :  
```bash
pip install pyttsx3
```

### **Problème : L’agent ne capte pas la voix**
❌ **Erreur** : Aucun son détecté  
✔ **Solution** :  
1. Vérifie ton micro avec une autre application  
2. Ajuste le bruit ambiant avant de parler  
3. Redémarre l’agent et essaye à nouveau  

---

## **🔗 Ressources**
🔹 [Ollama - Documentation](https://ollama.ai/docs)  
🔹 [Python SpeechRecognition](https://pypi.org/project/SpeechRecognition/)  
🔹 [pyttsx3 - Text-to-Speech](https://pypi.org/project/pyttsx3/)  

---

## **📜 Licence**
Projet open-source sous **MIT License**. Libre à toi de le modifier et l’améliorer ! 🚀  

---
