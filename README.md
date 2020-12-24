# mse_auto_checking_slides_vaganov
## Таск-трекер: [[link]](https://github.com/moevm/mse_auto_checking_slides_vaganov/projects/1)  
Скринкаст первой итерации (прототип): [[link]](https://yadi.sk/i/59qktvtQMWLZyw)  
Скринкаст второй итерации: [[link]](https://yadi.sk/i/zHboIWHajNgnKg)  
#### Инструкция запуска приложения:  
Протестировано для Ubuntu 18.04.  
```bash
git clone https://github.com/moevm/mse_auto_checking_slides_vaganov.git
cd mse_auto_checking_slides_vaganov/
sudo apt install git curl python3-pip python3-venv npm mongodb
python3 -m pip install virtualenv
python3 -m venv venv
source venv/bin/activate
curl -sL https://deb.nodesource.com/setup_10.x | sudo -E bash -
sudo apt install -y nodejs
./act.sh -i -b -d
```  
Далее в терминале отобразится адрес, по которому можно получить доступ к приложению. До первой проверки необходимо установить критерии. Для debug-режима по умолчанию доступен пользователь admin с паролем admin.
 
