# HA_Ragtech_UPS

Integração para nobreak Ragtech para HomeAssistant


Agradecimentos:
* Ao Christian: pela nova arquitetura: https://github.com/clyra/nhs2mqtt

## Arquitetura (v0)

* O Nobreak (UPS) conecta via USB ao computador (ou via VM)
* O Software original do fabricante deve estar instalado na máquina, VM ou container
* Esta integração consulta os dados do equipamento e disponibiliza via API Rest na porta 5000
* O HomeAssistant através da integração RESTful acessa os dados

## Como configurar (v0)

1. Tenha o software do fabricante operacional e funcionando (chamarei de Server)
2. Obtenha o IP do computador/VM que o Server está operando
3. Configure o IP do Server no arquivo Proxy/server.py
4. Suba o container (pasta Proxy), este container aceitará conexões na porta 5000
5. Configure o Home Assistant para utilizar a integração RESTful de acordo com arquivo `configuration_ups.yaml`

Locais com IPs para mudar ou anotar:
* `configuration_ups.yaml`: IP do Proxy
* `Proxy/server.py`: IP do Servidor

# Contributing (EN)

We welcome contributions to the project! However, it's important to note that none of Ragtech's intellectual property (IP), including their proprietary code, algorithms, or documentation, should be used or included in any contributions.

Please adhere to the following guidelines when making contributions:

1. **Respect Intellectual Property:** Do not use or include any Ragtech IP in your contributions. This includes code snippets, algorithms, documentation, or any other proprietary information owned by Ragtech.

2. **Original Work:** Ensure that your contributions are your original work and do not infringe upon any intellectual property rights of others.

3. **License Compatibility:** Make sure that your contributions are compatible with the project's open-source license, if applicable.

Please be aware that contributions that violate these guidelines, including those that contain any Ragtech IP, will not be accepted. If, by any chance, such contributions are mistakenly accepted, they will be promptly identified and removed from the project. We genuinely appreciate your understanding and cooperation in assisting us in maintaining a compliant and respectful project environment.

Additionally, we want to emphasize that individuals who have signed any non-disclosure agreements (NDAs) with Ragtech or have had access to Ragtech software development kits (SDKs) are not permitted to contribute to this project's library. We must respect legal obligations and protect intellectual property rights. If you fall into this category, we kindly request that you refrain from making this contributions. Thank you for your understanding and adherence to this policy.

If you have any questions or need further clarification, please reach out to the project maintainers. Thank you for your interest in contributing to the project!