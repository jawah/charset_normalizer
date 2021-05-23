# coding: utf-8
from functools import lru_cache

from charset_normalizer.constant import UNICODE_RANGES_ZIP, UNICODE_RANGES_NAMES, UNICODE_SECONDARY_RANGE_KEYWORD


@lru_cache(maxsize=8192)
def find_letter_type(letter):
    """
    This method is intended to associate a single character with a range name from the unicode table
    :param str letter: Shall be a unique char
    :return: Associated unicode range designation
    :rtype: Union[str, None]
    """
    if len(letter) != 1:
        raise IOError('Trying to associate multiple char <{}> to a single unicode range'.format(letter))

    for u_name, u_range in UNICODE_RANGES_ZIP.items():

        if ord(letter) in u_range:
            return u_name

    return None


@lru_cache(maxsize=8192)
def is_accentuated(letter):
    """
    Verify if a latin letter is accentuated, unicode point of view.
    :param str letter: Letter to check
    :return: True if accentuated, else False
    :rtype: bool
    """
    if len(letter) != 1:
        raise IOError('Trying to determine accentuated state of multiple char <{}>'.format(letter))
    return 192 <= ord(letter) <= 383


@lru_cache(maxsize=512)
def get_range_id(range_name):
    return UNICODE_RANGES_NAMES.index(range_name)


@lru_cache(maxsize=8192)
def is_latin(letter):
    """
    Verify if a letter is Latin based
    :param str letter:
    :return:
    """
    return 'Latin' in (find_letter_type(letter) or '')


@lru_cache(maxsize=8192)
def is_punc(letter):
    """
    Verify if a letter is a sort of punctuation sign
    :param str letter:
    :return:
    """
    if letter.isspace():
        return True
    r_name = find_letter_type(letter)
    return r_name is not None and \
           ("Punctuation" in r_name or
           'Forms' in r_name or
           letter in set('%º¯—–‒‐⁃«‹?!;.:^$¥*»£¹¿~ª؟©±¡{}[]|½⅓⅔¼¾⅕⅖⅗⅘⅙⅚⅐⅛⅜⅝⅞⅑⅒™℠¬‼⁇❝❞¶⁋√↑↓�¤©`¨'))


@lru_cache(maxsize=8192)
def is_cjk(letter):
    """
    Verify if a letter is part of a CJK unicode range
    :param str letter:
    :return:
    """
    return 'CJK' in (find_letter_type(letter) or '')


def unravel_suspicious_ranges(str_len, encountered_unicode_range_occurrences):
    """
    :param int str_len:
    :param dict encountered_unicode_range_occurrences:
    :return:
    """
    items = encountered_unicode_range_occurrences.items()
    s_ = 0

    # print(encountered_unicode_range_occurrences)

    for k, v in items:
        k_ = k.lower()
        if (
                'latin' not in k_ and 'general punctuation' not in k_ and 'symbols and punctuation' not in k_ and 'cjk' not in k_) or 'latin extended' in k_ or 'latin-1 supplement' in k_:
            if v / str_len < 0.09:
                if len(encountered_unicode_range_occurrences.keys()) <= 2 and 'latin-1 supplement' in k_:
                    continue
                if 'halfwidth and fullwidth forms' in k_ and any(['CJK' in el for el in encountered_unicode_range_occurrences.keys()]):
                    continue
                if 'hiragana' in k_ or 'katakana' in k_:
                    continue
                # print('suspicious', k_, 'with', v)
                s_ += v

    return s_


@lru_cache(maxsize=8192)
def is_simplified_chinese(character):
    return character in "㐷㐹㐽㑇㑈㑔㑩㓆㓥㓰㔉㖊㖞㗷㘎㚯㛀㛟㛠㛣㛤㛿㟆㟜㟥㡎㤘㤽㥪㧏㧐㧑㧟㧰㨫㭎㭏㭣㭤㭴㱩㱮㲿㳔㳕㳠㳡㳢㳽㴋㶉㶶㶽㺍㻅㻏㻘䀥䁖䂵䃅䅉䅟䅪䇲䉤䌶䌷䌸䌹䌺䌻䌼䌽䌾䌿䍀䍁䍠䎬䏝䑽䓓䓕䓖䓨䗖䘛䘞䙊䙌䙓䜣䜤䜥䜧䜩䝙䞌䞍䞎䞐䟢䢀䢁䢂䥺䥽䥾䥿䦀䦁䦂䦃䦅䦆䦶䦷䩄䭪䯃䯄䯅䲝䲞䲟䲠䲡䲢䲣䴓䴔䴕䴖䴗䴘䴙䶮与专业丛东丝丢两严丧个临为丽举义乌乐乔习乡书买乱争亏亘亚产亩亲亵亸亿仅从仑仓仪们众优会伛伞伟传伡伣伤伥伦伧伪伫体佥侠侣侥侦侧侨侩侪侬侭俣俦俨俩俪俫俭债倾偬偻偾偿傤傥傧储傩儿兑兖兰关兴兹养兽冁内冈册写军农冯冲决况冻净凄凉减凑凛凤凫凭凯击凿刍刘则刚创删别刬刭刹刽刾刿剀剂剐剑剥剧劝办务劢动励劲劳势勋勚匀匦匮区医华协单卖卢卤卧卫却卺厅历厉压厌厍厐厕厢厣厦厨厩厮县叁参叆叇双发变叙叠号叹叽吃吓吕吗吣吨听启吴呐呒呓呕呖呗员呙呛呜咏咙咛咝咤响哑哒哓哔哕哗哙哜哝哟唇唛唝唠唡唢唤啧啬啭啮啯啰啴啸喷喽喾嗫嗳嘘嘤嘱噜嚣团园囱围囵国图圆圣圹场坂坏块坚坛坜坝坞坟坠垄垅垆垒垦垩垫垭垯垱垲垴埘埙埚埯堑堕塆墙壮声壳壶壸处备复够夫头夹夺奁奂奋奖奥妆妇妈妩妪妫姗姹娄娅娆娇娈娱娲娴婳婴婵婶媪媭嫒嫔嫱嬷孙学孪宁宝实宠审宪宫宽宾寝对寻导寿将尔尘尝尧尴尽层屃屉届属屡屦屿岁岂岖岗岘岙岚岛岭岳岽岿峃峄峡峣峤峥峦峰崂崃崄崭嵘嵚嵝巅巩巯币帅师帏帐帜带帧帮帱帻帼幂幞并庄庆床庐庑库应庙庞废庼廪开异弃弑张弥弪弯弹强归当录彝彟彦彨彻径徕忆忏忧忾怀态怂怃怄怅怆怜总怼怿恋恒恤恳恶恸恹恺恻恼恽悦悫悬悭悮悯惊惧惨惩惫惬惭惮惯愠愤愦慑慭懑懒懔戆戋戏戗战戬戯户扑执扩扪扫扬扰抚抛抟抠抡抢护报抬抵担拟拢拣拥拦拧拨择挚挛挜挝挞挟挠挡挢挣挤挥挦捝捞损捡换捣掳掴掷掸掺掼揽揾揿搀搁搂搄搅携摄摅摆摇摈摊撄撑撵撷撸撺擜擞攒敌教敚敛敩数斋斓斩断无旧时旷旸昙昵昼昽显晋晒晓晔晕晖暂暅暧术机杀杂权条来杨杩构枞枢枣枥枧枨枪枫枭柠查柽栀栅标栈栉栊栋栌栎栏树栖样栾桠桡桢档桤桥桦桧桨桩桪梦梼梾梿检棁棂椁椝椟椠椢椤椫椭椮楼榄榅榇榈榉榝槚槛槟槠横樯樱橥橱橹橼檩欢欤欧歼殁殇残殒殓殚殡殴毁毂毕毙毡毵毶氇气氢氩氲汇汉污汤汹沟没沣沤沥沦沧沨沩沪泞泪泶泷泸泺泻泼泽泾洁洒洼浃浅浆浇浈浉浊测浍济浏浐浑浒浓浔浕涚涛涝涞涟涠涡涢涣涤润涧涨涩渊渌渍渎渐渑渔渖渗温湾湿溁溃溅溆溇滗滚滞滟滠满滢滤滥滦滨滩滪潆潇潋潍潜潴澛澜濑濒灏灭灯灵灶灾灿炀炉炖炜炝点炼炽烁烂烃烛烟烦烧烨烩烫烬热焕焖焘煴爱爷牍牦牵牺犊状犷犸犹狈狝狞独狭狮狯狰狱狲猃猎猕猡猪猫猬献獭玑玙玚玛玮环现玱玺珐珑珰珲琎琏琐琼瑶瑷瑸璎瓒瓯电画畅畴疖疗疟疠疡疬疭疮疯疱疴痈痉痒痖痨痪痫痴瘅瘆瘗瘘瘪瘫瘾瘿癞癣癫皂皑皱皲盏盐监盖盗盘眍眦眬睁睐睑瞆瞒瞩矫矶矾矿砀码砖砗砚砜砺砻砾础硁硕硖硗硙硚硵硷碍碛碜碱礼祃祎祢祯祷祸禀禄禅离秃秆秘积称秽秾稆税稣稳穑穞穷窃窍窎窑窜窝窥窦窭竖竞笃笋笔笕笺笼笾筚筛筜筝筹筼签筿简箓箦箧箨箩箪箫篑篓篮篯篱簖籁籴类籼粜粝粤粪粮粽糁糇糍紧絷縆纟纠纡红纣纤纥约级纨纩纪纫纬纭纮纯纰纱纲纳纴纵纶纷纸纹纺纻纼纽纾线绀绁绂练组绅细织终绉绊绋绌绍绎经绐绑绒结绔绕绖绗绘给绚绛络绝绞统绠绡绢绣绤绥绦继绨绩绪绫绬续绮绯绰绱绲绳维绵绶绷绸绹绺绻综绽绾绿缀缁缂缃缄缅缆缇缈缉缊缋缌缍缎缏缐缑缒缓缔缕编缗缘缙缚缛缜缝缞缟缠缡缢缣缤缥缦缧缨缩缪缫缬缭缮缯缰缱缲缳缴缵罂网罗罚罢罴羁羟羡群翘翙翚耢耧耸耻聂聋职聍联聩聪肃肠肤肮肾肿胀胁胄胆背胧胨胪胫胶脉脍脏脐脑脓脔脚脱脶脸腘腭腻腼腽腾膑膻臜舆舣舰舱舻艰艳艺节芈芗芜芦芲芸苁苇苈苋苌苍苎苏苔苘茎茏茑茔茕茧荆荙荚荛荜荝荞荟荠荡荣荤荥荦荧荨荩荪荫荬荭荮药莅莱莲莳莴莶获莸莹莺莼萚萝萤营萦萧萨葱蒀蒇蒉蒋蒌蒏蓝蓟蓠蓣蓥蓦蔂蔷蔹蔺蔼蕰蕲蕴薮藓蘖虏虑虚虬虮虱虽虾虿蚀蚁蚂蚃蚕蚝蚬蛊蛎蛏蛮蛰蛱蛲蛳蛴蜕蜗蝇蝈蝉蝎蝼蝾螀螨蟏衅衔补衬衮袄袅袆袜袭袯装裆裈裢裣裤裥褛褴襕见观觃规觅视觇览觉觊觋觌觍觎觏觐觑觞触觯訚詟誉誊讠计订讣认讥讦讧讨让讪讫讬训议讯记讱讲讳讴讵讶讷许讹论讻讼讽设访诀证诂诃评诅识诇诈诉诊诋诌词诎诏诐译诒诓诔试诖诗诘诙诚诛诜话诞诟诠诡询诣诤该详诧诨诩诪诫诬语诮误诰诱诲诳说诵诶请诸诹诺读诼诽课诿谀谁谂调谄谅谆谇谈谉谊谋谌谍谎谏谐谑谒谓谔谕谖谗谘谙谚谛谜谝谞谟谠谡谢谣谤谥谦谧谨谩谪谫谬谭谮谯谰谱谲谳谴谵谶豮贝贞负贠贡财责贤败账货质贩贪贫贬购贮贯贰贱贲贳贴贵贶贷贸费贺贻贼贽贾贿赀赁赂赃资赅赆赇赈赉赊赋赌赍赎赏赐赑赒赓赔赕赖赗赘赙赚赛赜赝赞赟赠赡赢赣赪赵赶趋趱趸跃跄跞践跶跷跸跹跻踌踪踬踯蹑蹒蹰蹿躏躜躯车轧轨轩轪轫转轭轮软轰轱轲轳轴轵轶轷轸轹轺轻轼载轾轿辀辁辂较辄辅辆辇辈辉辊辋辌辍辎辏辐辑辒输辔辕辖辗辘辙辚辞辩辫边辽达迁过迈运还这进远违连迟迩迳迹选逊递逦逻遗遥邓邝邬邮邹邺邻郏郐郑郓郦郧郸酂酝酦酱酽酾酿释鉴銮錾钅钆钇针钉钊钋钌钍钎钏钐钑钒钓钔钕钖钗钘钙钚钛钜钝钞钟钠钡钢钣钤钥钦钧钨钩钪钫钬钭钮钯钰钱钲钳钴钵钶钷钸钹钺钻钼钽钾钿铀铁铂铃铄铅铆铇铈铉铊铋铌铍铎铏铐铑铒铓铔铕铖铗铘铙铚铛铜铝铞铟铠铡铢铣铤铥铦铧铨铩铪铫铬铭铮铯铰铱铲铳铴铵银铷铸铹铺铻铼铽链铿销锁锂锃锄锅锆锇锈锉锊锋锌锍锎锏锐锑锒锓锔锕锖锗锘错锚锛锜锝锞锟锠锡锢锣锤锥锦锧锨锩锪锫锬锭键锯锰锱锲锳锴锵锶锷锸锹锺锻锼锽锾锿镀镁镂镃镄镅镆镇镈镉镊镋镌镍镎镏镐镑镒镓镔镕镖镗镘镙镚镛镜镝镞镠镡镢镣镤镥镦镧镨镩镪镫镬镭镮镯镰镱镲镳镴镵镶长门闩闪闫闬闭问闯闰闱闲闳间闵闶闷闸闹闺闻闼闽闾闿阀阁阂阃阄阅阆阇阈阉阊阋阌阍阎阏阐阑阒阓阔阕阖阗阘阙阚阛队阳阴阵阶际陆陇陈陉陕陦陧陨险随隐隶隽难雏雠雳雾霁霉霡霭靓靔静靥鞑鞒鞯鞲韦韧韨韩韪韫韬韵页顶顷顸项顺须顼顽顾顿颀颁颂颃预颅领颇颈颉颊颋颌颍颎颏颐频颒颓颔颕颖颗题颙颚颛颜额颞颟颠颡颢颣颤颥颦颧风飏飐飑飒飓飔飕飖飗飘飙飚飞飨餍饣饤饥饦饧饨饩饪饫饬饭饮饯饰饱饲饳饴饵饶饷饸饹饺饻饼饽饾饿馀馁馂馃馄馅馆馇馈馉馊馋馌馍馎馏馐馑馒馓馔馕马驭驮驯驰驱驲驳驴驵驶驷驸驹驺驻驼驽驾驿骀骁骂骃骄骅骆骇骈骉骊骋验骍骎骏骐骑骒骓骔骕骖骗骘骙骚骛骜骝骞骟骠骡骢骣骤骥骦骧髅髋髌鬓鬶魇魉鱼鱽鱾鱿鲀鲁鲂鲃鲄鲅鲆鲇鲈鲉鲊鲋鲌鲍鲎鲏鲐鲑鲒鲓鲔鲕鲖鲗鲘鲙鲚鲛鲜鲝鲞鲟鲠鲡鲢鲣鲤鲥鲦鲧鲨鲩鲪鲫鲬鲭鲮鲯鲰鲱鲲鲳鲴鲵鲶鲷鲸鲹鲺鲻鲼鲽鲾鲿鳀鳁鳂鳃鳄鳅鳆鳇鳈鳉鳊鳋鳌鳍鳎鳏鳐鳑鳒鳓鳔鳕鳖鳗鳘鳙鳚鳛鳜鳝鳞鳟鳠鳡鳢鳣鳤鸟鸠鸡鸢鸣鸤鸥鸦鸧鸨鸩鸪鸫鸬鸭鸮鸯鸰鸱鸲鸳鸴鸵鸶鸷鸸鸹鸺鸻鸼鸽鸾鸿鹀鹁鹂鹃鹄鹅鹆鹇鹈鹉鹊鹋鹌鹍鹎鹏鹐鹑鹒鹓鹔鹕鹖鹗鹘鹙鹚鹛鹜鹝鹞鹟鹠鹡鹢鹣鹤鹥鹦鹧鹨鹩鹪鹫鹬鹭鹮鹯鹰鹱鹲鹳鹴鹾麦麸麹麺黄黉黡黩黪黾鼋鼌鼍鼗鼹齄齐齑齿龀龁龂龃龄龅龆龇龈龉龊龋龌龙龚龛龟鿎鿏鿒鿔𠀾𠆲𠆿𠇹𠉂𠉗𠊉𠋆𠚳𠛅𠛆𠛾𠡠𠮶𠯟𠯠𠰱𠰷𠱞𠲥𠴛𠴢𠵸𠵾𡋀𡋗𡋤𡍣𡒄𡝠𡞋𡞱𡠟𡥧𡭜𡭬𡳃𡳒𡶴𡸃𡺃𡺄𢋈𢗓𢘙𢘝𢘞𢙏𢙐𢙑𢙒𢙓𢛯𢠁𢢐𢧐𢫊𢫞𢫬𢬍𢬦𢭏𢽾𣃁𣆐𣈣𣍨𣍯𣍰𣎑𣏢𣐕𣐤𣑶𣒌𣓿𣔌𣗊𣗋𣗙𣘐𣘓𣘴𣘷𣚚𣞎𣨼𣭤𣯣𣱝𣲗𣲘𣳆𣶩𣶫𣶭𣷷𣸣𣺼𣺽𣽷𤆡𤆢𤇃𤇄𤇭𤇹𤈶𤈷𤊀𤊰𤋏𤎺𤎻𤙯𤝢𤞃𤞤𤠋𤦀𤩽𤳄𤶊𤶧𤻊𤽯𤾀𤿲𥁢𥅘𥅴𥅿𥆧𥇢𥎝𥐟𥐯𥐰𥐻𥞦𥧂𥩟𥩺𥫣𥬀𥬞𥬠𥭉𥮋𥮜𥮾𥱔𥹥𥺅𥺇𦈈𦈉𦈋𦈌𦈎𦈏𦈐𦈑𦈒𦈓𦈔𦈕𦈖𦈗𦈘𦈙𦈚𦈛𦈜𦈝𦈞𦈟𦈠𦈡𦍠𦛨𦝼𦟗𦨩𦰏𦰴𦶟𦶻𦻕𦼖𧉐𧉞𧌥𧏖𧏗𧑏𧒭𧜭𧝝𧝧𧮪𧳕𧹑𧹒𧹓𧹔𧹕𧹖𧹗𧿈𨀁𨀱𨁴𨂺𨄄𨅛𨅫𨅬𨉗𨐅𨐆𨐇𨐈𨐉𨐊𨑹𨟳𨠨𨡙𨡺𨤰𨰾𨰿𨱀𨱁𨱂𨱃𨱄𨱅𨱆𨱇𨱈𨱉𨱊𨱋𨱌𨱍𨱎𨱏𨱐𨱑𨱒𨱓𨱔𨱕𨱖𨷿𨸀𨸁𨸂𨸃𨸄𨸅𨸆𨸇𨸉𨸊𨸋𨸌𨸎𨸘𨸟𩏼𩏽𩏾𩏿𩐀𩓋𩖕𩖖𩖗𩙥𩙦𩙧𩙨𩙩𩙪𩙫𩙬𩙭𩙮𩙯𩙰𩟿𩠀𩠁𩠂𩠃𩠅𩠆𩠇𩠈𩠉𩠊𩠋𩠌𩠎𩠏𩠠𩡖𩧦𩧨𩧩𩧪𩧫𩧬𩧭𩧮𩧯𩧰𩧱𩧲𩧳𩧴𩧵𩧶𩧸𩧺𩧻𩧼𩧿𩨀𩨁𩨂𩨃𩨄𩨅𩨆𩨇𩨈𩨉𩨊𩨋𩨌𩨍𩨎𩨏𩨐𩩈𩬣𩬤𩭹𩯒𩰰𩲒𩴌𩽹𩽺𩽻𩽼𩽽𩽾𩽿𩾀𩾁𩾂𩾃𩾄𩾅𩾆𩾇𩾈𩾊𩾋𩾌𩾎𪉂𪉃𪉄𪉅𪉆𪉈𪉉𪉊𪉋𪉌𪉍𪉎𪉏𪉐𪉑𪉒𪉓𪉔𪉕𪎈𪎉𪎊𪎋𪎌𪎍𪑅𪔭𪚏𪚐𪜎𪞝𪟎𪟝𪠀𪠟𪠡𪠳𪠵𪠸𪠺𪠽𪡀𪡃𪡋𪡏𪡛𪡞𪡺𪢌𪢐𪢒𪢕𪢖𪢠𪢮𪢸𪣆𪣒𪣻𪤄𪤚𪥠𪥫𪥰𪥿𪧀𪧘𪨊𪨗𪨧𪨩𪨶𪨷𪨹𪩇𪩎𪩘𪩛𪩷𪩸𪪏𪪑𪪞𪪴𪪼𪫌𪫡𪫷𪫺𪬚𪬯𪭝𪭢𪭧𪭯𪭵𪭾𪮃𪮋𪮖𪮳𪮶𪯋𪰶𪱥𪱷𪲎𪲔𪲛𪲮𪳍𪳗𪴙𪵑𪵣𪵱𪶄𪶒𪶮𪷍𪷽𪸕𪸩𪹀𪹠𪹳𪹹𪺣𪺪𪺭𪺷𪺸𪺻𪺽𪻐𪻨𪻲𪻺𪼋𪼴𪽈𪽝𪽪𪽭𪽮𪽴𪽷𪾔𪾢𪾣𪾦𪾸𪿊𪿞𪿫𪿵𫀌𫀓𫀨𫀬𫀮𫁂𫁟𫁡𫁱𫁲𫁳𫁷𫁺𫂃𫂆𫂈𫂖𫂿𫃗𫄙𫄚𫄛𫄜𫄝𫄞𫄟𫄠𫄡𫄢𫄣𫄤𫄥𫄦𫄧𫄨𫄩𫄪𫄫𫄬𫄭𫄮𫄯𫄰𫄱𫄲𫄳𫄴𫄵𫄶𫄷𫄸𫄹𫅅𫅗𫅥𫅭𫅼𫆏𫆝𫆫𫇘𫇛𫇪𫇭𫇴𫇽𫈉𫈎𫈟𫈵𫉁𫉄𫊪𫊮𫊸𫊹𫊻𫋇𫋌𫋲𫋷𫋹𫋻𫌀𫌇𫌋𫌨𫌪𫌫𫌬𫌭𫌯𫍐𫍙𫍚𫍛𫍜𫍝𫍞𫍟𫍠𫍡𫍢𫍣𫍤𫍥𫍦𫍧𫍨𫍩𫍪𫍫𫍬𫍭𫍮𫍯𫍰𫍱𫍲𫍳𫍴𫍵𫍶𫍷𫍸𫍹𫍺𫍻𫍼𫍽𫍾𫍿𫎆𫎌𫎦𫎧𫎨𫎩𫎪𫎫𫎬𫎭𫎱𫎳𫎸𫎺𫏃𫏆𫏋𫏌𫏐𫏑𫏕𫏞𫏨𫐄𫐅𫐆𫐇𫐈𫐉𫐊𫐋𫐌𫐍𫐎𫐏𫐐𫐑𫐒𫐓𫐔𫐕𫐖𫐗𫐘𫐙𫐷𫑘𫑡𫑷𫓥𫓦𫓧𫓨𫓩𫓪𫓫𫓬𫓭𫓮𫓯𫓰𫓱𫓲𫓳𫓴𫓵𫓶𫓷𫓸𫓹𫓺𫓻𫓼𫓽𫓾𫓿𫔀𫔁𫔂𫔃𫔄𫔅𫔆𫔇𫔈𫔉𫔊𫔋𫔌𫔍𫔎𫔏𫔐𫔑𫔒𫔓𫔔𫔕𫔖𫔭𫔮𫔯𫔰𫔲𫔴𫔵𫔶𫔽𫕚𫕥𫕨𫖃𫖅𫖇𫖑𫖒𫖓𫖔𫖕𫖖𫖪𫖫𫖬𫖭𫖮𫖯𫖰𫖱𫖲𫖳𫖴𫖵𫖶𫖷𫖸𫖹𫖺𫗇𫗈𫗉𫗊𫗋𫗚𫗞𫗟𫗠𫗡𫗢𫗣𫗤𫗥𫗦𫗧𫗨𫗩𫗪𫗫𫗬𫗭𫗮𫗯𫗰𫗱𫗳𫗴𫗵𫘛𫘜𫘝𫘞𫘟𫘠𫘡𫘣𫘤𫘥𫘦𫘧𫘨𫘩𫘪𫘫𫘬𫘭𫘮𫘯𫘰𫘱𫘽𫙂𫚈𫚉𫚊𫚋𫚌𫚍𫚎𫚏𫚐𫚑𫚒𫚓𫚔𫚕𫚖𫚗𫚘𫚙𫚚𫚛𫚜𫚝𫚞𫚟𫚠𫚡𫚢𫚣𫚤𫚥𫚦𫚧𫚨𫚩𫚪𫚫𫚬𫚭𫛚𫛛𫛜𫛝𫛞𫛟𫛠𫛡𫛢𫛣𫛤𫛥𫛦𫛧𫛨𫛩𫛪𫛫𫛬𫛭𫛮𫛯𫛰𫛱𫛲𫛳𫛴𫛵𫛶𫛷𫛸𫛹𫛺𫛻𫛼𫛽𫛾𫜀𫜁𫜂𫜃𫜄𫜅𫜊𫜑𫜒𫜓𫜔𫜕𫜙𫜟𫜨𫜩𫜪𫜫𫜬𫜭𫜮𫜯𫜰𫜲𫜳𫝈𫝋𫝦𫝧𫝨𫝩𫝪𫝫𫝬𫝭𫝮𫝵𫞅𫞗𫞚𫞛𫞝𫞠𫞡𫞢𫞣𫞥𫞦𫞧𫞨𫞩𫞷𫟃𫟄𫟅𫟆𫟇𫟑𫟕𫟞𫟟𫟠𫟡𫟢𫟤𫟥𫟦𫟫𫟬𫟲𫟳𫟴𫟵𫟶𫟷𫟸𫟹𫟺𫟻𫟼𫟽𫟾𫟿𫠀𫠁𫠂𫠅𫠆𫠇𫠈𫠊𫠋𫠌𫠏𫠐𫠑𫠒𫠖𫠜𫢸𫮃𫰛𫶇𫷷𫸩𬀩𬬭𬬻𬭊𬭛𬭳𬭶𬶋𬶍𬶏𬶟𬸪"


@lru_cache(maxsize=8192)
def is_traditional_chinese(character):
    return character in "㑮㑯㑳㑶㒓㓄㓨㔋㖮㗲㗿㘉㘓㘔㘚㛝㜄㜏㜐㜗㜢㜷㞞㟺㠏㢗㢝㥮㦎㦛㦞㨻㩋㩜㩳㩵㪎㯤㰙㵗㵾㶆㷍㷿㸇㹽㺏㺜㻶㿖㿗㿧䀉䀹䁪䁻䂎䃮䅐䅳䆉䉑䉙䉬䉲䉶䊭䊷䊺䋃䋔䋙䋚䋦䋹䋻䋼䋿䌈䌋䌖䌝䌟䌥䌰䍤䍦䍽䎙䎱䕤䕳䖅䗅䗿䙔䙡䙱䚩䛄䛳䜀䜖䝭䝻䝼䞈䞋䞓䟃䟆䟐䠆䠱䡐䡩䡵䢨䤤䥄䥇䥑䥗䥩䥯䥱䦘䦛䦟䦯䦳䧢䪊䪏䪗䪘䪴䪾䫀䫂䫟䫴䫶䫻䫾䬓䬘䬝䬞䬧䭀䭃䭑䭔䭿䮄䮝䮞䮠䮫䮰䮳䮾䯀䯤䰾䱀䱁䱙䱧䱬䱰䱷䱸䱽䲁䲅䲖䲘䲰䳜䳢䳤䳧䳫䴉䴋䴬䴱䴴䴽䵳䵴䶕䶲丟並乾亂亙亞佇佈佔併來侖侶侷俁係俓俔俠俥俬倀倆倈倉個們倖倫倲偉偑側偵偽傌傑傖傘備傢傭傯傳傴債傷傾僂僅僉僑僕僞僥僨僱價儀儁儂億儈儉儎儐儔儕儘償儣優儭儲儷儸儺儻儼兇兌兒兗內兩冊冑冪凈凍凙凜凱別刪剄則剋剎剗剛剝剮剴創剷剾劃劇劉劊劌劍劏劑劚勁勑動務勛勝勞勢勣勩勱勳勵勸勻匭匯匱區協卹卻卽厙厠厤厭厲厴參叄叢吒吳吶呂咼員哯唄唓唚唸問啓啞啟啢喎喚喪喫喬單喲嗆嗇嗊嗎嗚嗩嗰嗶嗹嘆嘍嘓嘔嘖嘗嘜嘩嘪嘮嘯嘰嘳嘵嘸嘺嘽噁噅噓噚噝噞噠噥噦噯噲噴噸噹嚀嚇嚌嚐嚕嚙嚛嚥嚦嚧嚨嚮嚲嚳嚴嚶嚽囀囁囂囃囅囈囉囌囑囒囪圇國圍園圓圖團圞垵埡埬埰執堅堊堖堚堝堯報場塊塋塏塒塗塚塢塤塵塹塿墊墜墮墰墲墳墶墻墾壇壈壋壎壓壗壘壙壚壜壞壟壠壢壣壩壪壯壺壼壽夠夢夥夾奐奧奩奪奬奮奼妝姍姦娛婁婡婦婭媈媧媯媰媼媽嫋嫗嫵嫺嫻嫿嬀嬃嬇嬈嬋嬌嬙嬡嬣嬤嬦嬪嬰嬸嬻孃孄孆孇孋孌孎孫學孻孾孿宮寀寠寢實寧審寫寬寵寶將專尋對導尷屆屍屓屜屢層屨屩屬岡峯峴島峽崍崑崗崙崢崬嵐嵗嵼嵾嶁嶄嶇嶈嶔嶗嶘嶠嶢嶧嶨嶮嶴嶸嶹嶺嶼嶽巊巋巒巔巖巗巘巰巹帥師帳帶幀幃幓幗幘幝幟幣幩幫幬幹幺幾座庫廁廂廄廈廎廕廚廝廟廠廡廢廣廧廩廬廳弒弔弳張強彃彆彈彌彎彔彙彞彠彥彫彲彷彿後徑從徠復徵徹徿恆恥悅悞悵悶悽惡惱惲惻愛愜愨愴愷愻愾慄態慍慘慚慟慣慤慪慫慮慳慶慺慼慾憂憊憐憑憒憖憚憢憤憫憮憲憶憸憹懀懇應懌懍懎懞懟懣懤懨懲懶懷懸懺懼懾戀戇戔戧戩戰戱戲戶拋拚挩挱挾捨捫捱捲掃掄掆掗掙掚掛採揀揚換揮揯損搖搗搵搶摋摐摑摜摟摯摳摶摺摻撈撊撏撐撓撝撟撣撥撧撫撲撳撻撾撿擁擄擇擊擋擓擔據擟擠擡擣擫擬擯擰擱擲擴擷擺擻擼擽擾攄攆攋攏攔攖攙攛攜攝攢攣攤攪攬敎敓敗敘敵數斂斃斅斆斕斬斷斸於旂旣昇時晉晝暈暉暘暢暫曄曆曇曉曊曏曖曠曥曨曬書會朥朧朮東杴枴柵柺査桱桿梔梖梘條梟梲棄棊棖棗棟棡棧棲棶椏椲楇楊楓楨業極榘榦榪榮榲榿構槍槓槤槧槨槫槮槳槶槼樁樂樅樑樓標樞樠樢樣樤樧樫樳樸樹樺樿橈橋機橢橫橯檁檉檔檜檟檢檣檭檮檯檳檵檸檻檾櫃櫅櫓櫚櫛櫝櫞櫟櫠櫥櫧櫨櫪櫫櫬櫱櫳櫸櫺櫻欄欅欇權欍欏欐欑欒欓欖欘欞欽歎歐歟歡歲歷歸歿殘殞殢殤殨殫殭殮殯殰殲殺殻殼毀毆毊毿氂氈氌氣氫氬氭氳氾汎汙決沒沖況泝洩洶浹涇涗涼淒淚淥淨淩淪淵淶淺渙減渢渦測渾湊湋湞湧湯溈準溝溡溫溮溳溼滄滅滌滎滙滬滯滲滷滸滻滾滿漁漊漚漢漣漬漲漵漸漿潁潑潔潕潙潚潛潣潤潯潰潷潿澀澅澆澇澐澗澠澤澦澩澬澮澱澾濁濃濄濆濕濘濚濛濜濟濤濧濫濰濱濺濼濾濿瀂瀃瀅瀆瀇瀉瀋瀏瀕瀘瀝瀟瀠瀦瀧瀨瀰瀲瀾灃灄灍灑灒灕灘灙灝灡灣灤灧灩災為烏烴無煇煉煒煙煢煥煩煬煱熂熅熉熌熒熓熗熚熡熱熲熾燁燈燉燒燙燜營燦燬燭燴燶燻燼燾爃爄爇爍爐爖爛爥爧爭爲爺爾牀牆牘牴牽犖犛犞犢犧狀狹狽猌猙猶猻獁獃獄獅獊獎獨獩獪獫獮獰獱獲獵獷獸獺獻獼玀玁珼現琱琺琿瑋瑒瑣瑤瑩瑪瑲瑻瑽璉璊璝璡璣璦璫璯環璵璸璼璽璾瓄瓊瓏瓔瓕瓚瓛甌甕產産甦甯畝畢畫異畵當畼疇疊痙痠痮痾瘂瘋瘍瘓瘞瘡瘧瘮瘱瘲瘺瘻療癆癇癉癐癒癘癟癡癢癤癥癧癩癬癭癮癰癱癲發皁皚皟皰皸皺盃盜盞盡監盤盧盨盪眝眞眥眾睍睏睜睞睪瞘瞜瞞瞤瞭瞶瞼矇矉矑矓矚矯硃硜硤硨硯碕碙碩碭碸確碼碽磑磚磠磣磧磯磽磾礄礆礎礒礙礦礪礫礬礮礱祇祕祘祿禍禎禕禡禦禪禮禰禱禿秈稅稈稏稜稟種稱穀穇穌積穎穠穡穢穩穫穭窩窪窮窯窵窶窺竄竅竇竈竊竚竪竱競筆筍筧筴箇箋箏節範築篋篔篘篠篤篩篳篸簀簂簍簑簞簡簢簣簫簹簽簾籃籅籋籌籔籙籛籜籟籠籤籩籪籬籮籲粵糉糝糞糧糰糲糴糶糹糺糾紀紂約紅紆紇紈紉紋納紐紓純紕紖紗紘紙級紛紜紝紟紡紬紮細紱紲紳紵紹紺紼紿絀絁終絃組絅絆絍絎結絕絙絛絝絞絡絢絥給絧絨絰統絲絳絶絹絺綀綁綃綆綇綈綉綋綌綏綐綑經綖綜綞綟綠綡綢綣綫綬維綯綰綱網綳綴綵綸綹綺綻綽綾綿緄緇緊緋緍緑緒緓緔緗緘緙線緝緞緟締緡緣緤緦編緩緬緮緯緰緱緲練緶緷緸緹緻縈縉縊縋縍縎縐縑縕縗縛縝縞縟縣縧縫縬縭縮縰縱縲縳縴縵縶縷縸縹縺總績繂繃繅繆繈繏繐繒繓織繕繚繞繟繡繢繨繩繪繫繬繭繮繯繰繳繶繷繸繹繻繼繽繾繿纁纇纈纊續纍纏纓纔纖纗纘纚纜缽罃罈罌罎罰罵罷羅羆羈羋羣羥羨義羵羶習翬翹翽耬耮聖聞聯聰聲聳聵聶職聹聻聽聾肅脅脈脛脣脥脩脫脹腎腖腡腦腪腫腳腸膃膕膚膞膠膢膩膹膽膾膿臉臍臏臗臘臚臟臠臢臥臨臺與興舉舊舘艙艣艤艦艫艱艷芻茲荊莊莖莢莧菕華菴菸萇萊萬萴萵葉葒著葝葤葦葯葷蒍蒐蒓蒔蒕蒞蒭蒼蓀蓆蓋蓧蓮蓯蓴蓽蔔蔘蔞蔣蔥蔦蔭蔯蔿蕁蕆蕎蕒蕓蕕蕘蕝蕢蕩蕪蕭蕳蕷蕽薀薆薈薊薌薑薔薘薟薦薩薰薳薴薵薹薺藉藍藎藝藥藪藭藶藷藹藺蘀蘄蘆蘇蘊蘋蘚蘞蘟蘢蘭蘺蘿虆處虛虜號虧虯蛺蛻蜆蝕蝟蝦蝨蝸螄螞螢螮螻螿蟂蟄蟈蟎蟘蟜蟣蟬蟯蟲蟳蟶蟻蠀蠁蠅蠆蠍蠐蠑蠔蠙蠟蠣蠦蠨蠱蠶蠻蠾衆衊術衕衚衛衝衹袞裊裏補裝裡製複褌褘褲褳褸褻襀襆襇襉襏襓襖襗襘襝襠襤襪襬襯襰襲襴襵覆覈見覎規覓視覘覛覡覥覦親覬覯覲覷覹覺覼覽覿觀觴觶觸訁訂訃計訊訌討訐訑訒訓訕訖託記訛訜訝訞訟訢訣訥訨訩訪設許訴訶診註証詀詁詆詊詎詐詑詒詓詔評詖詗詘詛詞詠詡詢詣試詩詫詬詭詮詰話該詳詵詷詼詿誂誄誅誆誇誋誌認誑誒誕誘誚語誠誡誣誤誥誦誨說誫説誰課誳誴誶誷誹誺誼誾調諂諄談諉請諍諏諑諒論諗諛諜諝諞諡諢諣諤諥諦諧諫諭諮諯諰諱諳諴諶諷諸諺諼諾謀謁謂謄謅謆謉謊謎謏謐謔謖謗謙謚講謝謠謡謨謫謬謭謯謱謳謸謹謾譁譂譅譆證譊譎譏譑譖識譙譚譜譞譟譨譫譭譯議譴護譸譽譾讀讅變讋讌讎讒讓讕讖讚讜讞豈豎豐豔豬豵豶貓貗貙貝貞貟負財貢貧貨販貪貫責貯貰貲貳貴貶買貸貺費貼貽貿賀賁賂賃賄賅資賈賊賑賒賓賕賙賚賜賝賞賟賠賡賢賣賤賦賧質賫賬賭賰賴賵賺賻購賽賾贃贄贅贇贈贉贊贋贍贏贐贑贓贔贖贗贚贛贜赬趕趙趨趲跡踐踰踴蹌蹔蹕蹟蹣蹤蹳蹺蹻躂躉躊躋躍躎躑躒躓躕躘躚躝躡躥躦躪軀軉車軋軌軍軏軑軒軔軕軗軛軜軟軤軨軫軬軲軷軸軹軺軻軼軾軿較輄輅輇輈載輊輋輒輓輔輕輖輗輛輜輝輞輟輢輥輦輨輩輪輬輮輯輳輷輸輻輾輿轀轂轄轅轆轇轉轊轍轎轐轔轗轟轠轡轢轣轤辦辭辮辯農迴逕這連週進遊運過達違遙遜遞遠遡適遱遲遷選遺遼邁還邇邊邏邐郟郵鄆鄉鄒鄔鄖鄟鄧鄭鄰鄲鄳鄴鄶鄺酇酈醃醜醞醟醣醫醬醱醶釀釁釃釅釋釐釒釓釔釕釗釘釙釚針釟釣釤釦釧釨釩釲釳釵釷釹釺釾鈀鈁鈃鈄鈅鈆鈇鈈鈉鈋鈍鈎鈐鈑鈒鈔鈕鈖鈗鈛鈞鈠鈡鈣鈥鈦鈧鈮鈯鈰鈲鈳鈴鈷鈸鈹鈺鈽鈾鈿鉀鉁鉅鉆鉈鉉鉋鉍鉑鉔鉕鉗鉚鉛鉝鉞鉠鉢鉤鉦鉬鉭鉳鉶鉷鉸鉺鉻鉽鉾鉿銀銁銂銃銅銈銊銍銏銑銓銖銘銚銛銜銠銣銥銦銨銩銪銫銬銱銳銶銷銹銻銼鋁鋂鋃鋅鋇鋉鋌鋏鋒鋗鋙鋝鋟鋠鋣鋤鋥鋦鋨鋩鋪鋭鋮鋯鋰鋱鋶鋸鋼錀錁錂錄錆錇錈錏錐錒錕錘錙錚錛錜錝錟錠錡錢錤錥錦錨錩錫錮錯録錳錶錸錼錽鍀鍁鍃鍄鍅鍆鍇鍈鍉鍊鍋鍍鍒鍔鍘鍚鍛鍠鍤鍥鍩鍬鍮鍰鍵鍶鍺鍼鍾鎂鎄鎇鎈鎊鎌鎍鎔鎖鎘鎙鎚鎛鎝鎞鎡鎢鎣鎦鎧鎩鎪鎬鎭鎮鎯鎰鎲鎳鎵鎶鎷鎸鎿鏃鏆鏇鏈鏉鏌鏍鏐鏑鏗鏘鏚鏜鏝鏞鏟鏡鏢鏤鏥鏦鏨鏰鏵鏷鏹鏺鏽鏾鐃鐄鐇鐈鐋鐍鐎鐏鐐鐒鐓鐔鐗鐘鐙鐝鐠鐥鐦鐧鐨鐪鐫鐮鐯鐲鐳鐵鐶鐸鐺鐼鐽鐿鑀鑄鑉鑊鑌鑑鑒鑔鑕鑞鑠鑣鑥鑪鑭鑰鑱鑲鑴鑷鑹鑼鑽鑾鑿钁钂長門閂閃閆閈閉開閌閍閎閏閐閑閒間閔閗閘閝閞閡閣閤閥閨閩閫閬閭閱閲閵閶閹閻閼閽閾閿闃闆闇闈闊闋闌闍闐闑闒闓闔闕闖關闞闠闡闢闤闥阪陘陝陞陣陰陳陸陽隉隊階隕際隨險隯隱隴隸隻雋雖雙雛雜雞離難雲電霢霣霧霼霽靂靄靆靈靉靚靜靝靦靧靨鞀鞏鞝鞦鞽鞾韁韃韆韉韋韌韍韓韙韚韛韜韝韞韠韻響頁頂頃項順頇須頊頌頍頎頏預頑頒頓頗領頜頡頤頦頫頭頮頰頲頴頵頷頸頹頻頽顂顃顅顆題額顎顏顒顓顔顗願顙顛類顢顣顥顧顫顬顯顰顱顳顴風颭颮颯颰颱颳颶颷颸颺颻颼颾飀飄飆飈飋飛飠飢飣飥飦飩飪飫飭飯飱飲飴飵飶飼飽飾飿餃餄餅餉養餌餎餏餑餒餓餔餕餖餗餘餚餛餜餞餡餦餧館餪餫餬餭餱餳餵餶餷餸餺餼餾餿饁饃饅饈饉饊饋饌饑饒饗饘饜饞饟饠饢馬馭馮馯馱馳馴馹馼駁駃駊駎駐駑駒駔駕駘駙駚駛駝駞駟駡駢駤駧駩駫駭駰駱駶駸駻駿騁騂騃騄騅騉騊騌騍騎騏騔騖騙騚騜騝騟騠騤騧騪騫騭騮騰騱騴騵騶騷騸騻騼騾驀驁驂驃驄驅驊驋驌驍驏驓驕驗驙驚驛驟驢驤驥驦驨驪驫骯髏髒體髕髖髮鬆鬍鬖鬚鬠鬢鬥鬧鬨鬩鬮鬱鬹魎魘魚魛魟魢魥魦魨魯魴魵魷魺魽鮁鮃鮄鮅鮆鮊鮋鮍鮎鮐鮑鮒鮓鮕鮚鮜鮝鮞鮟鮣鮤鮦鮪鮫鮭鮮鮯鮰鮳鮵鮶鮸鮺鮿鯀鯁鯄鯆鯇鯉鯊鯒鯔鯕鯖鯗鯛鯝鯞鯡鯢鯤鯧鯨鯪鯫鯬鯰鯱鯴鯶鯷鯽鯾鯿鰁鰂鰃鰆鰈鰉鰋鰌鰍鰏鰐鰑鰒鰓鰕鰛鰜鰟鰠鰣鰤鰥鰦鰧鰨鰩鰫鰭鰮鰱鰲鰳鰵鰷鰹鰺鰻鰼鰽鰾鱂鱄鱅鱆鱇鱈鱉鱊鱒鱔鱖鱗鱘鱝鱟鱠鱢鱣鱤鱧鱨鱭鱮鱯鱲鱷鱸鱺鳥鳧鳩鳬鳲鳳鳴鳶鳷鳼鳽鳾鴀鴃鴅鴆鴇鴉鴐鴒鴔鴕鴗鴛鴜鴝鴞鴟鴣鴥鴦鴨鴮鴯鴰鴲鴳鴴鴷鴻鴽鴿鵁鵂鵃鵊鵐鵑鵒鵓鵚鵜鵝鵟鵠鵡鵧鵩鵪鵫鵬鵮鵯鵰鵲鵷鵾鶄鶇鶉鶊鶌鶒鶓鶖鶗鶘鶚鶡鶥鶦鶩鶪鶬鶭鶯鶰鶲鶴鶹鶺鶻鶼鶿鷀鷁鷂鷄鷅鷈鷉鷊鷐鷓鷔鷖鷗鷙鷚鷣鷤鷥鷦鷨鷩鷫鷯鷲鷳鷴鷷鷸鷹鷺鷽鷿鸂鸇鸊鸋鸌鸏鸕鸗鸘鸚鸛鸝鸞鹵鹹鹺鹼鹽麗麥麨麩麪麫麬麯麲麳麴麵麷麼黃黌點黨黲黴黶黷黽黿鼂鼉鼕鼴齇齊齋齎齏齒齔齕齗齙齜齟齠齡齣齦齧齩齪齬齭齯齰齲齴齶齷齾龍龎龐龑龓龔龕龜龭龯鿁鿓𠁞𠌥𠏢𠐊𠗣𠞆𠠎𠬙𠽃𠿕𡂡𡃄𡃕𡃤𡄔𡄣𡅏𡅯𡑭𡓁𡓾𡔖𡞵𡟫𡠹𡡎𡢃𡮉𡮣𡳳𡸗𡹬𡻕𡽗𡾱𡿖𢍰𢠼𢣐𢣚𢣭𢤩𢤱𢤿𢯷𢶒𢶫𢷬𢷮𢹿𢺳𣈶𣋋𣍐𣙎𣜬𣝕𣞻𣠩𣠲𣯩𣯴𣯶𣽏𣾷𣿉𤁣𤄷𤅶𤑳𤑹𤒎𤒻𤓌𤓩𤘀𤛮𤛱𤜆𤠮𤢟𤢻𤩂𤪺𤫩𤬅𤳷𤳸𤷃𤸫𤺔𥊝𥌃𥏝𥕥𥖅𥖲𥗇𥜐𥜰𥞵𥢢𥢶𥢷𥨐𥪂𥯤𥴨𥴼𥵃𥵊𥶽𥸠𥻦𥼽𥽖𥾯𥿊𦀖𦂅𦃄𦃩𦅇𦅈𦆲𦒀𦔖𦘧𦟼𦠅𦡝𦢈𦣎𦧺𦪙𦪽𦱌𦾟𧎈𧒯𧔥𧕟𧜗𧜵𧝞𧞫𧟀𧡴𧢄𧦝𧦧𧩕𧩙𧩼𧫝𧬤𧭈𧭹𧳟𧵳𧶔𧶧𧷎𧸘𧹈𧽯𨂐𨄣𨅍𨆪𨇁𨇞𨇤𨇰𨇽𨈊𨈌𨊰𨊸𨊻𨋢𨌈𨍰𨎌𨎮𨏠𨏥𨞺𨟊𨢿𨣈𨣞𨣧𨤻𨥛𨥟𨦫𨧀𨧜𨧰𨧱𨨏𨨛𨨢𨩰𨪕𨫒𨬖𨭆𨭎𨭖𨭸𨮂𨮳𨯅𨯟𨰃𨰋𨰥𨰲𨲳𨳑𨳕𨴗𨴹𨵩𨵸𨶀𨶏𨶮𨶲𨷲𨼳𨽏𩀨𩅙𩎖𩎢𩏂𩏠𩏪𩏷𩑔𩒎𩓣𩓥𩔑𩔳𩖰𩗀𩗓𩗴𩘀𩘝𩘹𩘺𩙈𩚛𩚥𩚩𩚵𩛆𩛌𩛡𩛩𩜇𩜦𩜵𩝔𩝽𩞄𩞦𩞯𩟐𩟗𩠴𩡣𩡺𩢡𩢴𩢸𩢾𩣏𩣑𩣫𩣵𩣺𩤊𩤙𩤲𩤸𩥄𩥇𩥉𩥑𩦠𩧆𩭙𩯁𩯳𩰀𩰹𩳤𩴵𩵦𩵩𩵹𩶁𩶘𩶰𩶱𩷰𩸃𩸄𩸡𩸦𩻗𩻬𩻮𩼶𩽇𩿅𩿤𩿪𪀖𪀦𪀾𪁈𪁖𪂆𪃍𪃏𪃒𪃧𪄆𪄕𪅂𪆷𪇳𪈼𪉸𪋿𪌭𪍠𪓰𪔵𪘀𪘯𪙏𪟖𪷓𫒡𫜦"


@lru_cache(maxsize=8192)
def is_suspiciously_successive_range(range_name_a, range_name_b):
    """
    Verify if range B encountered just after range A is considered suspicious
    :param str range_name_a: Unicode range A
    :param str range_name_b: Unicode range B
    :return: True if suspicious else False
    :rtype: bool
    """
    if range_name_a is None or range_name_b is None:
        return True

    dec_range_name_a, dec_range_name_b = range_name_a.split(), range_name_b.split()

    if range_name_a == range_name_b:
        return False

    if 'Latin' in range_name_a and 'Latin' in range_name_b:
        return False

    for el in dec_range_name_a:
        if el in dec_range_name_b:
            return False

    if range_name_a in ['Katakana', 'Hiragana'] and 'CJK' in range_name_b:
        return False

    if 'CJK' in range_name_a and range_name_b in ['Katakana', 'Hiragana']:
        return False

    if range_name_a in ['Katakana', 'Hiragana'] and range_name_b in ['Katakana', 'Hiragana']:
        return False

    return True


def classification(word):
    """
    :param str word:
    :return:
    """
    cla_ = dict()

    for el in word:
        if el.isspace():
            raise IOError('Classification should not be invoked with sentences !')
        u_name = find_letter_type(el)
        if u_name is None:
            u_name = 'Unknown'
        if u_name not in cla_:
            cla_[u_name] = 0
        cla_[u_name] += 1

    return cla_


@lru_cache(maxsize=8192)
def is_range_secondary(u_range):
    """
    Determine if a unicode range name is not a primary range by search specific keyword in range name
    :param str u_range: Unicode range name
    :return: True if secondary else False
    :rtype: bool
    """
    try:
        get_range_id(u_range)
    except ValueError:
        return True

    for keyword in UNICODE_SECONDARY_RANGE_KEYWORD:
        if keyword in u_range:
            return True

    return False


def part_punc(word):
    """
    Determine how much of the word is composed of punc sign
    :param str word:
    :return: Ratio special letter VS len of the word
    :rtype: float
    """
    return [is_punc(el) for el in word].count(True) / len(word)


def part_accent(word):
    """
    Determine how much of the word is composed of accentuated letter
    :param word:
    :return: Ratio accentuated letter VS len of the word
    :rtype: float
    """
    return [is_accentuated(el) for el in word].count(True) / len(word)


def word_to_range_list(word):
    """
    :param str word:
    :return: Produce a list containing for each letter in word it's unicode range name
    :rtype: list[str]
    """
    return [find_letter_type(el) for el in word]


def word_to_range_continue(word):
    """
    :param str word:
    :return: List of tuple (unicode range with occ) continuously encountered in a word
    :rtype: list[tuple[str, int]]
    """
    l_ = list()

    for el in word:
        u_name = find_letter_type(el)
        if len(l_) == 0:
            l_.append(
                (
                    u_name,
                    1
                )
            )
        else:
            if is_suspiciously_successive_range(u_name, l_[-1][0]) is True:
                l_.append(
                    (
                        u_name,
                        1
                    )
                )
            else:
                l_[-1] = (
                    u_name,
                    l_[-1][1]+1
                )

    return l_


def part_lonely_range(word):
    """
    :param str word:
    :return:
    """
    return [u_occ_cont == 1 for u_name, u_occ_cont in word_to_range_continue(word)].count(True) / len(word)


def list_by_range(letters):
    """
    Sort letters by unicode range in a dict
    :param list[str] letters:
    :return: Letters by unicode range
    :rtype: dict
    """
    by_ranges = dict()

    for l in letters:
        u_range = find_letter_type(l)

        s_ = False

        for range_name, letters in by_ranges.items():
            if is_suspiciously_successive_range(range_name, u_range) is False:
                by_ranges[range_name].append(l)
                s_ = True
                break

        if s_ is False:
            if u_range not in by_ranges:
                by_ranges[u_range] = list()
            by_ranges[u_range].append(l)

    return by_ranges
