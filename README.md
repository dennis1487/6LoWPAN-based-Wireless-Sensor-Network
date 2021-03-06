# 基於6LoWPAN無線感測網路之無人飛行器資料收集系統

這是一個基於6LoWPAN協定的無人飛行器無線感測網路資料收集系統，感測節點使用6LoWPAN協定組成無線感測網路，節點之間則使用MQTT協定傳送資料，其中某幾個感測節點會成為MQTT broker，其他節點則會固定將資料傳到broker節點。無人飛行器只需跟broker節點連線，並接收資料將收集到的資料即時透過4G網路匯集至Google試算表上，讓後端使用者可以透過Google API取得並運用資料。

## sensor node

當sensor node開始啟動時，我們必須考慮到一個情況，broker有沒有正常運作? 若broker有正常運作，border router只須與broker連線；若broker沒有正常運作，則由border router自己來當broker，與各個sensor node進行連線並收集資料。

* Sensor node主要功能

1. Lowpan_Up

當sensor node啟動時，會自動建立IEEE 802.15.4的wpan層以及可執行IPv6的lowpan層。

2. Request_Mode_A

當sensor node啟動後，會發送udp封包給broker，並等待broker回傳訊息，以此確認broker是否啟動。若sensor node 傳送封包後5秒內沒收到訊息(timeout=5)，則會重新發送封包；當封包傳送超過6次都沒收到broker訊息則停止傳送封包，休息30秒後才再度傳送，並以此作為循環。若休息次數超過3次則進入Request_Mode_B。

3. Request_Mode_B

若sensor node得知地面上的broker沒有啟動的話，則停止傳送udp封包給地面broker，改等待無人飛行器傳送udp封包給自己(意即broker為無人飛行器)，以確認無人飛行器上的broker有啟動。

4. Data_Collection

將sensor感測到的數據以及感測的時間點儲存起來，每5秒儲存1次。

5. Data_Publish

將sensor node收集到的資料，透過MQTT傳送到broker。訊息的QoS=1才能確保離線訊息能被broker保留。

## broker

* broker主要功能

1. Lowpan_Up

當sensor node啟動時，會自動建立IEEE 802.15.4的wpan層以及可執行IPv6的lowpan層。

2. Mosqitto

當Broker啟動時，執行MQTT server。

3. Response

等待sensor node或無人飛行器傳送封包，若接收到封包則傳送一個訊息回去。

## border router

根據無線感測網路的組網情況，border router有不一樣的作用。若border router能接收到broker的udp封包，則於該broker組網並接收資料。但若沒有接收到broker的udp封包，則由border router作為broker，負責發送udp封包與各個sensor node進行連線並收集資料。當資料收集完畢後，border router把資料透過wifi/4G傳送至後端電腦。

* Border router主要功能

1. Lowpan_Up

當sensor node啟動時，會自動建立IEEE 802.15.4的wpan層以及可執行IPv6的lowpan層。

2. Request_Mode_A

Border router會發送udp封包給broker，並等待broker回傳訊息，以此確認broker是否啟動。若sensor node 傳送封包後5秒內沒收到訊息(timeout=5)，則會重新發送封包；當封包傳送超過6次都沒收到broker訊息則停止傳送封包，並進入Request_Mode_B。

3. Request_Mode_B

當Border router確認broker不存在時，將改傳送udp封包給sensor node。

4. Data_Subscribe

從broker(地面或自己)接收訂閱的資料，其中Qos=1、clean_session=False，並且要給broker一個固定的client_id，才能確保異常斷線後再次連線能接收到離線訊息。

5. Alternative_Broker

若地面Broker無法正常運作，Border router將啟動broker，接收publisher傳播的資料。(只有在進入Request_Mode_B才有此功能)

6. Post_to_Sheet

將訂閱到資料透過4G網路上傳至Google試算表。

