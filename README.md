# HA_Ragtech_UPS

Integração para nobreak Ragtech para HomeAssistant


Agradecimentos:
* Ao Christian: pela nova arquitetura: https://github.com/clyra/nhs2mqtt

## Arquitetura

* O Nobreak (UPS) conecta via USB ao computador (ou via VM)
* Os dados são lidos da serial e enviados ao HomeAssistant via mqtt

## Como configurar (v0)

* O Nobreak (UPS) conecta via USB ao computador (ou via VM)
* Anote a porta (COMx ou /dev/ttyAMCx)
* Crie o arquivo de configuração com base no sample
* Atualize o arquivo com a porta serial e os dados do mqtt
* Suba o container mapeando a porta serial, ou execute o server.py

# Contributing (EN)

We welcome contributions to the project! However, it's important to note that none of Ragtech's intellectual property (IP), including their proprietary code, algorithms, or documentation, should be used or included in any contributions.

Please adhere to the following guidelines when making contributions:

1. **Respect Intellectual Property:** Do not use or include any Ragtech IP in your contributions. This includes code snippets, algorithms, documentation, or any other proprietary information owned by Ragtech.

2. **Original Work:** Ensure that your contributions are your original work and do not infringe upon any intellectual property rights of others.

3. **License Compatibility:** Make sure that your contributions are compatible with the project's open-source license, if applicable.

Please be aware that contributions that violate these guidelines, including those that contain any Ragtech IP, will not be accepted. If, by any chance, such contributions are mistakenly accepted, they will be promptly identified and removed from the project. We genuinely appreciate your understanding and cooperation in assisting us in maintaining a compliant and respectful project environment.

Additionally, we want to emphasize that individuals who have signed any non-disclosure agreements (NDAs) with Ragtech or have had access to Ragtech software development kits (SDKs) are not permitted to contribute to this project's library. We must respect legal obligations and protect intellectual property rights. If you fall into this category, we kindly request that you refrain from making this contributions. Thank you for your understanding and adherence to this policy.

If you have any questions or need further clarification, please reach out to the project maintainers. Thank you for your interest in contributing to the project!