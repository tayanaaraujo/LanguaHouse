ATUALIZAR O REPOSITÓRIO REMOTO

1. Navegue até o diretório do projeto local
No terminal ou prompt de comando, vá até o diretório onde está o seu projeto local:
cd /caminho/para/seu/projeto

3. Verifique se você está na branch correta
Use o comando abaixo para verificar em qual branch você está.
git branch

Se você não estiver na branch correta, troque para ela com o comando:
git checkout nome-da-branch

3. Puxe as atualizações do repositório remoto
Antes de fazer suas alterações, é uma boa prática garantir que você tenha as últimas atualizações do repositório remoto (no GitHub). Use:
git pull origin nome-da-branch
Isso puxa as alterações mais recentes do repositório remoto para o seu repositório local.

4. Faça as alterações no seu projeto
Agora você pode fazer as alterações desejadas no seu código, arquivos ou configuração.

5. Adicione os arquivos modificados ao Git
Depois de fazer suas alterações, adicione os arquivos modificados para serem "commitados":
git add .

git add caminho/para/arquivo

6. Faça o commit das suas alterações
Depois de adicionar os arquivos, faça o commit com uma mensagem explicativa:
git commit -m "Descrição das alterações feitas"

7. Envie as alterações para o GitHub
Agora, você precisa enviar as suas alterações para o repositório remoto no GitHub:
git push origin nome-da-branch

ATUALIZAR O REPOSITÓRIO LOCAL (SEU PC)
1. Entre no diretório do repositóriO
cd caminho-meu-repositorio
2. Atualize o repositório
git pull origin main

SE HOUVER CONFLITO 
Passos para sobrescrever arquivos locais/ CMD 
1. Busque as mudanças mais recentes sem aplicá-las ainda:
git fetch origin
2. Force o repositório local a se alinhar completamente com o remoto (substituindo tudo):
git reset --hard origin/main


Se perder o arquivo config.py
DB_CONFIG = {
    'MYSQL_HOST' : 'BD-ACD',
    'MYSQL_USER' : 'BD070324137',
    'MYSQL_PASSWORD' : 'Lamqt1',
    'MYSQL_DB' : 'BD070324137'
}

