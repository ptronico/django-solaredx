.. _login:

Login SolarEDX
==============

Idealmente o sistema de autenticação deverá ser implementado utilizando o 
protocolo `OAuth2 <http://oauth.net/2/>`_. Enquanto isso, será utilizado 
um sistema de autenticação simplificado, descrito abaixo:

Sistema de login simplificado
-----------------------------

O sistema de login simplificado consiste em uma requisição POST com destino
a um endereço específico no SolarEDX. O próprio usuário deverá efetuar essa 
requisição, pois o SolarEDX irá autenticar a sua sessão de acesso. Um 
formulário html com campos ocultos é capaz de tornar essa requisição tão
simples quanto o clique em um link.

Essa requisição deverá ser enviada para o endereço ``/solaredx/login/``. 
Deverão ser enviados dois parâmetros, sendo eles o ``username`` do usuário 
e o ``token`` de autenticação.

O ``token`` de autenticação deverá ser gerado utilizando `HMAC 
<http://en.wikipedia.org/wiki/Hash-based_message_authentication_code>`_ 
e função de hash SHA1. O valor a ser criptografado deve ser o ``username`` 
do usuário. A ``key`` (chave) deverá ser fornecida pelo Solar. Por fim, 
o resultado da criptografia deverá ser codificado em hexadecimal.

.. note::

    Use a extensão `Postman <https://chrome.google.com/webstore/detail/postman-rest-client/fdmmgilgnpjigdojojpjoooidkmcomcm?hl=en>`_ do Chrome para fazer um 
    login teste.