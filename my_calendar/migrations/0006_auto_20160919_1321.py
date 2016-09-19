# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-09-19 11:21
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('my_calendar', '0005_auto_20160918_1307'),
    ]

    operations = [
        migrations.AlterField(
            model_name='eventcustomsettings',
            name='timezone',
            field=models.IntegerField(default=436),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='timezone',
            field=models.IntegerField(choices=[(1, 'Africa/Abidjan'), (2, 'Africa/Accra'), (3, 'Africa/Addis_Ababa'), (4, 'Africa/Algiers'), (5, 'Africa/Asmara'), (6, 'Africa/Bamako'), (7, 'Africa/Bangui'), (8, 'Africa/Banjul'), (9, 'Africa/Bissau'), (10, 'Africa/Blantyre'), (11, 'Africa/Brazzaville'), (12, 'Africa/Bujumbura'), (13, 'Africa/Cairo'), (14, 'Africa/Casablanca'), (15, 'Africa/Ceuta'), (16, 'Africa/Conakry'), (17, 'Africa/Dakar'), (18, 'Africa/Dar_es_Salaam'), (19, 'Africa/Djibouti'), (20, 'Africa/Douala'), (21, 'Africa/El_Aaiun'), (22, 'Africa/Freetown'), (23, 'Africa/Gaborone'), (24, 'Africa/Harare'), (25, 'Africa/Johannesburg'), (26, 'Africa/Juba'), (27, 'Africa/Kampala'), (28, 'Africa/Khartoum'), (29, 'Africa/Kigali'), (30, 'Africa/Kinshasa'), (31, 'Africa/Lagos'), (32, 'Africa/Libreville'), (33, 'Africa/Lome'), (34, 'Africa/Luanda'), (35, 'Africa/Lubumbashi'), (36, 'Africa/Lusaka'), (37, 'Africa/Malabo'), (38, 'Africa/Maputo'), (39, 'Africa/Maseru'), (40, 'Africa/Mbabane'), (41, 'Africa/Mogadishu'), (42, 'Africa/Monrovia'), (43, 'Africa/Nairobi'), (44, 'Africa/Ndjamena'), (45, 'Africa/Niamey'), (46, 'Africa/Nouakchott'), (47, 'Africa/Ouagadougou'), (48, 'Africa/Porto-Novo'), (49, 'Africa/Sao_Tome'), (50, 'Africa/Tripoli'), (51, 'Africa/Tunis'), (52, 'Africa/Windhoek'), (53, 'America/Adak'), (54, 'America/Anchorage'), (55, 'America/Anguilla'), (56, 'America/Antigua'), (57, 'America/Araguaina'), (58, 'America/Argentina/Buenos_Aires'), (59, 'America/Argentina/Catamarca'), (60, 'America/Argentina/Cordoba'), (61, 'America/Argentina/Jujuy'), (62, 'America/Argentina/La_Rioja'), (63, 'America/Argentina/Mendoza'), (64, 'America/Argentina/Rio_Gallegos'), (65, 'America/Argentina/Salta'), (66, 'America/Argentina/San_Juan'), (67, 'America/Argentina/San_Luis'), (68, 'America/Argentina/Tucuman'), (69, 'America/Argentina/Ushuaia'), (70, 'America/Aruba'), (71, 'America/Asuncion'), (72, 'America/Atikokan'), (73, 'America/Bahia'), (74, 'America/Bahia_Banderas'), (75, 'America/Barbados'), (76, 'America/Belem'), (77, 'America/Belize'), (78, 'America/Blanc-Sablon'), (79, 'America/Boa_Vista'), (80, 'America/Bogota'), (81, 'America/Boise'), (82, 'America/Cambridge_Bay'), (83, 'America/Campo_Grande'), (84, 'America/Cancun'), (85, 'America/Caracas'), (86, 'America/Cayenne'), (87, 'America/Cayman'), (88, 'America/Chicago'), (89, 'America/Chihuahua'), (90, 'America/Costa_Rica'), (91, 'America/Creston'), (92, 'America/Cuiaba'), (93, 'America/Curacao'), (94, 'America/Danmarkshavn'), (95, 'America/Dawson'), (96, 'America/Dawson_Creek'), (97, 'America/Denver'), (98, 'America/Detroit'), (99, 'America/Dominica'), (100, 'America/Edmonton'), (101, 'America/Eirunepe'), (102, 'America/El_Salvador'), (103, 'America/Fort_Nelson'), (104, 'America/Fortaleza'), (105, 'America/Glace_Bay'), (106, 'America/Godthab'), (107, 'America/Goose_Bay'), (108, 'America/Grand_Turk'), (109, 'America/Grenada'), (110, 'America/Guadeloupe'), (111, 'America/Guatemala'), (112, 'America/Guayaquil'), (113, 'America/Guyana'), (114, 'America/Halifax'), (115, 'America/Havana'), (116, 'America/Hermosillo'), (117, 'America/Indiana/Indianapolis'), (118, 'America/Indiana/Knox'), (119, 'America/Indiana/Marengo'), (120, 'America/Indiana/Petersburg'), (121, 'America/Indiana/Tell_City'), (122, 'America/Indiana/Vevay'), (123, 'America/Indiana/Vincennes'), (124, 'America/Indiana/Winamac'), (125, 'America/Inuvik'), (126, 'America/Iqaluit'), (127, 'America/Jamaica'), (128, 'America/Juneau'), (129, 'America/Kentucky/Louisville'), (130, 'America/Kentucky/Monticello'), (131, 'America/Kralendijk'), (132, 'America/La_Paz'), (133, 'America/Lima'), (134, 'America/Los_Angeles'), (135, 'America/Lower_Princes'), (136, 'America/Maceio'), (137, 'America/Managua'), (138, 'America/Manaus'), (139, 'America/Marigot'), (140, 'America/Martinique'), (141, 'America/Matamoros'), (142, 'America/Mazatlan'), (143, 'America/Menominee'), (144, 'America/Merida'), (145, 'America/Metlakatla'), (146, 'America/Mexico_City'), (147, 'America/Miquelon'), (148, 'America/Moncton'), (149, 'America/Monterrey'), (150, 'America/Montevideo'), (151, 'America/Montserrat'), (152, 'America/Nassau'), (153, 'America/New_York'), (154, 'America/Nipigon'), (155, 'America/Nome'), (156, 'America/Noronha'), (157, 'America/North_Dakota/Beulah'), (158, 'America/North_Dakota/Center'), (159, 'America/North_Dakota/New_Salem'), (160, 'America/Ojinaga'), (161, 'America/Panama'), (162, 'America/Pangnirtung'), (163, 'America/Paramaribo'), (164, 'America/Phoenix'), (165, 'America/Port-au-Prince'), (166, 'America/Port_of_Spain'), (167, 'America/Porto_Velho'), (168, 'America/Puerto_Rico'), (169, 'America/Rainy_River'), (170, 'America/Rankin_Inlet'), (171, 'America/Recife'), (172, 'America/Regina'), (173, 'America/Resolute'), (174, 'America/Rio_Branco'), (175, 'America/Santarem'), (176, 'America/Santiago'), (177, 'America/Santo_Domingo'), (178, 'America/Sao_Paulo'), (179, 'America/Scoresbysund'), (180, 'America/Sitka'), (181, 'America/St_Barthelemy'), (182, 'America/St_Johns'), (183, 'America/St_Kitts'), (184, 'America/St_Lucia'), (185, 'America/St_Thomas'), (186, 'America/St_Vincent'), (187, 'America/Swift_Current'), (188, 'America/Tegucigalpa'), (189, 'America/Thule'), (190, 'America/Thunder_Bay'), (191, 'America/Tijuana'), (192, 'America/Toronto'), (193, 'America/Tortola'), (194, 'America/Vancouver'), (195, 'America/Whitehorse'), (196, 'America/Winnipeg'), (197, 'America/Yakutat'), (198, 'America/Yellowknife'), (199, 'Antarctica/Casey'), (200, 'Antarctica/Davis'), (201, 'Antarctica/DumontDUrville'), (202, 'Antarctica/Macquarie'), (203, 'Antarctica/Mawson'), (204, 'Antarctica/McMurdo'), (205, 'Antarctica/Palmer'), (206, 'Antarctica/Rothera'), (207, 'Antarctica/Syowa'), (208, 'Antarctica/Troll'), (209, 'Antarctica/Vostok'), (210, 'Arctic/Longyearbyen'), (211, 'Asia/Aden'), (212, 'Asia/Almaty'), (213, 'Asia/Amman'), (214, 'Asia/Anadyr'), (215, 'Asia/Aqtau'), (216, 'Asia/Aqtobe'), (217, 'Asia/Ashgabat'), (218, 'Asia/Baghdad'), (219, 'Asia/Bahrain'), (220, 'Asia/Baku'), (221, 'Asia/Bangkok'), (222, 'Asia/Barnaul'), (223, 'Asia/Beirut'), (224, 'Asia/Bishkek'), (225, 'Asia/Brunei'), (226, 'Asia/Chita'), (227, 'Asia/Choibalsan'), (228, 'Asia/Colombo'), (229, 'Asia/Damascus'), (230, 'Asia/Dhaka'), (231, 'Asia/Dili'), (232, 'Asia/Dubai'), (233, 'Asia/Dushanbe'), (234, 'Asia/Gaza'), (235, 'Asia/Hebron'), (236, 'Asia/Ho_Chi_Minh'), (237, 'Asia/Hong_Kong'), (238, 'Asia/Hovd'), (239, 'Asia/Irkutsk'), (240, 'Asia/Jakarta'), (241, 'Asia/Jayapura'), (242, 'Asia/Jerusalem'), (243, 'Asia/Kabul'), (244, 'Asia/Kamchatka'), (245, 'Asia/Karachi'), (246, 'Asia/Kathmandu'), (247, 'Asia/Khandyga'), (248, 'Asia/Kolkata'), (249, 'Asia/Krasnoyarsk'), (250, 'Asia/Kuala_Lumpur'), (251, 'Asia/Kuching'), (252, 'Asia/Kuwait'), (253, 'Asia/Macau'), (254, 'Asia/Magadan'), (255, 'Asia/Makassar'), (256, 'Asia/Manila'), (257, 'Asia/Muscat'), (258, 'Asia/Nicosia'), (259, 'Asia/Novokuznetsk'), (260, 'Asia/Novosibirsk'), (261, 'Asia/Omsk'), (262, 'Asia/Oral'), (263, 'Asia/Phnom_Penh'), (264, 'Asia/Pontianak'), (265, 'Asia/Pyongyang'), (266, 'Asia/Qatar'), (267, 'Asia/Qyzylorda'), (268, 'Asia/Rangoon'), (269, 'Asia/Riyadh'), (270, 'Asia/Sakhalin'), (271, 'Asia/Samarkand'), (272, 'Asia/Seoul'), (273, 'Asia/Shanghai'), (274, 'Asia/Singapore'), (275, 'Asia/Srednekolymsk'), (276, 'Asia/Taipei'), (277, 'Asia/Tashkent'), (278, 'Asia/Tbilisi'), (279, 'Asia/Tehran'), (280, 'Asia/Thimphu'), (281, 'Asia/Tokyo'), (282, 'Asia/Tomsk'), (283, 'Asia/Ulaanbaatar'), (284, 'Asia/Urumqi'), (285, 'Asia/Ust-Nera'), (286, 'Asia/Vientiane'), (287, 'Asia/Vladivostok'), (288, 'Asia/Yakutsk'), (289, 'Asia/Yekaterinburg'), (290, 'Asia/Yerevan'), (291, 'Atlantic/Azores'), (292, 'Atlantic/Bermuda'), (293, 'Atlantic/Canary'), (294, 'Atlantic/Cape_Verde'), (295, 'Atlantic/Faroe'), (296, 'Atlantic/Madeira'), (297, 'Atlantic/Reykjavik'), (298, 'Atlantic/South_Georgia'), (299, 'Atlantic/St_Helena'), (300, 'Atlantic/Stanley'), (301, 'Australia/Adelaide'), (302, 'Australia/Brisbane'), (303, 'Australia/Broken_Hill'), (304, 'Australia/Currie'), (305, 'Australia/Darwin'), (306, 'Australia/Eucla'), (307, 'Australia/Hobart'), (308, 'Australia/Lindeman'), (309, 'Australia/Lord_Howe'), (310, 'Australia/Melbourne'), (311, 'Australia/Perth'), (312, 'Australia/Sydney'), (313, 'Canada/Atlantic'), (314, 'Canada/Central'), (315, 'Canada/Eastern'), (316, 'Canada/Mountain'), (317, 'Canada/Newfoundland'), (318, 'Canada/Pacific'), (319, 'Europe/Amsterdam'), (320, 'Europe/Andorra'), (321, 'Europe/Astrakhan'), (322, 'Europe/Athens'), (323, 'Europe/Belgrade'), (324, 'Europe/Berlin'), (325, 'Europe/Bratislava'), (326, 'Europe/Brussels'), (327, 'Europe/Bucharest'), (328, 'Europe/Budapest'), (329, 'Europe/Busingen'), (330, 'Europe/Chisinau'), (331, 'Europe/Copenhagen'), (332, 'Europe/Dublin'), (333, 'Europe/Gibraltar'), (334, 'Europe/Guernsey'), (335, 'Europe/Helsinki'), (336, 'Europe/Isle_of_Man'), (337, 'Europe/Istanbul'), (338, 'Europe/Jersey'), (339, 'Europe/Kaliningrad'), (340, 'Europe/Kiev'), (341, 'Europe/Kirov'), (342, 'Europe/Lisbon'), (343, 'Europe/Ljubljana'), (344, 'Europe/London'), (345, 'Europe/Luxembourg'), (346, 'Europe/Madrid'), (347, 'Europe/Malta'), (348, 'Europe/Mariehamn'), (349, 'Europe/Minsk'), (350, 'Europe/Monaco'), (351, 'Europe/Moscow'), (352, 'Europe/Oslo'), (353, 'Europe/Paris'), (354, 'Europe/Podgorica'), (355, 'Europe/Prague'), (356, 'Europe/Riga'), (357, 'Europe/Rome'), (358, 'Europe/Samara'), (359, 'Europe/San_Marino'), (360, 'Europe/Sarajevo'), (361, 'Europe/Simferopol'), (362, 'Europe/Skopje'), (363, 'Europe/Sofia'), (364, 'Europe/Stockholm'), (365, 'Europe/Tallinn'), (366, 'Europe/Tirane'), (367, 'Europe/Ulyanovsk'), (368, 'Europe/Uzhgorod'), (369, 'Europe/Vaduz'), (370, 'Europe/Vatican'), (371, 'Europe/Vienna'), (372, 'Europe/Vilnius'), (373, 'Europe/Volgograd'), (374, 'Europe/Warsaw'), (375, 'Europe/Zagreb'), (376, 'Europe/Zaporozhye'), (377, 'Europe/Zurich'), (378, 'GMT'), (379, 'Indian/Antananarivo'), (380, 'Indian/Chagos'), (381, 'Indian/Christmas'), (382, 'Indian/Cocos'), (383, 'Indian/Comoro'), (384, 'Indian/Kerguelen'), (385, 'Indian/Mahe'), (386, 'Indian/Maldives'), (387, 'Indian/Mauritius'), (388, 'Indian/Mayotte'), (389, 'Indian/Reunion'), (390, 'Pacific/Apia'), (391, 'Pacific/Auckland'), (392, 'Pacific/Bougainville'), (393, 'Pacific/Chatham'), (394, 'Pacific/Chuuk'), (395, 'Pacific/Easter'), (396, 'Pacific/Efate'), (397, 'Pacific/Enderbury'), (398, 'Pacific/Fakaofo'), (399, 'Pacific/Fiji'), (400, 'Pacific/Funafuti'), (401, 'Pacific/Galapagos'), (402, 'Pacific/Gambier'), (403, 'Pacific/Guadalcanal'), (404, 'Pacific/Guam'), (405, 'Pacific/Honolulu'), (406, 'Pacific/Johnston'), (407, 'Pacific/Kiritimati'), (408, 'Pacific/Kosrae'), (409, 'Pacific/Kwajalein'), (410, 'Pacific/Majuro'), (411, 'Pacific/Marquesas'), (412, 'Pacific/Midway'), (413, 'Pacific/Nauru'), (414, 'Pacific/Niue'), (415, 'Pacific/Norfolk'), (416, 'Pacific/Noumea'), (417, 'Pacific/Pago_Pago'), (418, 'Pacific/Palau'), (419, 'Pacific/Pitcairn'), (420, 'Pacific/Pohnpei'), (421, 'Pacific/Port_Moresby'), (422, 'Pacific/Rarotonga'), (423, 'Pacific/Saipan'), (424, 'Pacific/Tahiti'), (425, 'Pacific/Tarawa'), (426, 'Pacific/Tongatapu'), (427, 'Pacific/Wake'), (428, 'Pacific/Wallis'), (429, 'US/Alaska'), (430, 'US/Arizona'), (431, 'US/Central'), (432, 'US/Eastern'), (433, 'US/Hawaii'), (434, 'US/Mountain'), (435, 'US/Pacific'), (436, 'UTC')], default=436),
        ),
    ]
