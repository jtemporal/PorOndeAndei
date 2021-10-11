# Por Onde Andei: Edição Palestras

Esta API é escrita em Flask e usa Pandas, Folium e Auth0. Seu objetivo principal é servir um mapa de lugares que foram marcados.

## Requirements

- Python == `3.8.2`
- Flask == `2.0.0`
- Uma conta gratuita da Auth0, [cadastre-se gratuitamente aqui](https://a0.to/jtemporal-signup-for-auth0).

## Environment

```console
pip install -U pip
pip install -r requirements.txt
```

## Configurações

Crie o arquivo `.config` seguindo o arquivo de exemplo `.example.config` e preencha os valores faltantes.

## Rodando a API

### Em desenvolvimento

```console
flask run
```

Acesse: [http://127.0.0.1:5000/](http://127.0.0.1:5000/).

### Em produção

```
gunicorn app:app
```

Acesse: [http://127.0.0.1:8000/](http://127.0.0.1:8000/).

## Como Usar Esse Repo

### Navegando pelos branches

| Branch | Explicação |
| ----------- | ------- |
| `main` | Tudo que você precisa para fazer o setup inicial do projeto |
| `passo-1` | Vamos criar os dois primeiros endpoints, templates e rodar o projeto |
| `passo-2` | Vamos criar os dois endpoints que geram o nosso mapa e as funções que fazem ajustes de dados |
| `passo-3` | Vamos configurar a conta na Auth0 e proteger os endpoints |
| `passo-4` | Momento do deploy, configurar o código para o Heroku |
