import os

# a list of fonts for html
font_family = ['Abadi MT Condensed Light', 'Aharoni', 'Aharoni Bold', 'Aldhabi', 'AlternateGothic2 BT',
               'Andale Mono', 'Andalus', 'Angsana New', 'AngsanaUPC', 'Aparajita', 'Apple Chancery',
               'Arabic Typesetting', 'Arial', 'Arial Black', 'Arial narrow', 'Arial Nova', 'Arial Rounded MT Bold',
               'Arnoldboecklin', 'Avanta Garde', 'Bahnschrift', 'Bahnschrift Light', 'Bahnschrift SemiBold',
               'Bahnschrift SemiLight', 'Baskerville', 'Batang', 'BatangChe', 'Big Caslon', 'BIZ UDGothic',
               'BIZ UDMincho Medium', 'Blippo', 'Bodoni MT', 'Book Antiqua', 'Book Antiqua', 'Bookman',
               'Bradley Hand', 'Browallia New', 'BrowalliaUPC', 'Brush Script MT', 'Brush Script Std',
               'Brushstroke', 'Calibri', 'Calibri Light', 'Calisto MT', 'Cambodian', 'Cambria', 'Cambria Math',
               'Candara', 'Century Gothic', 'Chalkduster', 'Cherokee', 'Comic Sans', 'Comic Sans MS', 'Consolas',
               'Constantia', 'Copperplate', 'Copperplate Gothic Light', 'Copperplate Gothic Bold', 'Corbel',
               'Cordia New', 'CordiaUPC', 'Coronetscript', 'Courier', 'Courier New', 'DaunPenh', 'David',
               'DengXian', 'DFKai-SB', 'DFKai-SB', 'Didot', 'DilleniaUPC', 'DokChampa', 'Dotum', 'DotumChe',
               'Ebrima', 'Estrangelo Edessa', 'EucrosiaUPC', 'Euphemia', 'FangSong', 'Florence',
               'Franklin Gothic Medium', 'FrankRuehl', 'FreesiaUPC', 'Futara', 'Gabriola', 'Gadugi', 'Garamond',
               'Gautami', 'Geneva', 'Georgia', 'Georgia Pro', 'Gill Sans', 'Gill Sans Nova', 'Gisha',
               'Goudy Old Style', 'Gulim', 'GulimChe', 'Gungsuh', 'GungsuhChe', 'Hebrew', 'Hoefler Text',
               'HoloLens MDL2 Assets', 'Impact', 'Ink Free', 'IrisUPC', 'Iskoola Pota', 'Japanese', 'JasmineUPC',
               'Javanese Text', 'Jazz LET', 'KaiTi', 'Kalinga', 'Kartika', 'Khmer UI', 'KodchiangUPC', 'Kokila',
               'Korean', 'Lao', 'Lao UI', 'Latha', 'Leelawadee', 'Leelawadee UI', 'Leelawadee UI Semilight',
               'Levenim MT', 'LilyUPC', 'Lucida Bright', 'Lucida Console', 'Lucida Handwriting', 'Lucida Sans',
               'Lucida Sans Typewriter', 'Lucida Sans Unicode', 'Lucidatypewriter', 'Luminari', 'Malgun Gothic',
               'Malgun Gothic Semilight', 'Mangal', 'Marker Felt', 'Meiryo', 'Meiryo UI', 'Microsoft Himalaya',
               'Microsoft JhengHei', 'Microsoft JhengHei UI', 'Microsoft New Tai Lue', 'Microsoft PhagsPa',
               'Microsoft Sans Serif', 'Microsoft Tai Le', 'Microsoft Uighur', 'Microsoft YaHei',
               'Microsoft YaHei UI', 'Microsoft Yi Baiti', 'MingLiU', 'MingLiU_HKSCS', 'MingLiU_HKSCS',
               'MingLiU_HKSCS-ExtB', 'MingLiU_HKSCS-ExtB', 'MingLiU-ExtB', 'MingLiU-ExtB', 'Miriam', 'Monaco',
               'Mongolian Baiti', 'MoolBoran', 'MS Gothic', 'MS Mincho', 'MS PGothic', 'MS PMincho', 'MS UI Gothic',
               'MV Boli', 'Myanmar Text', 'Narkisim', 'Neue Haas Grotesk Text Pro', 'New Century Schoolbook',
               'News Gothic MT', 'Nirmala UI', 'No automatic language associations', 'Noto', 'NSimSun', 'Nyala',
               'Oldtown', 'Optima', 'Palatino', 'Palatino Linotype', 'papyrus', 'Parkavenue', 'Perpetua',
               'Plantagenet Cherokee', 'PMingLiU', 'Raavi', 'Rockwell', 'Rockwell Extra Bold', 'Rockwell Nova',
               'Rockwell Nova Cond', 'Rockwell Nova Extra Bold', 'Rod', 'Sakkal Majalla', 'Sanskrit Text',
               'Segoe MDL2 Assets', 'Segoe Print', 'Segoe Script', 'Segoe UI', 'Segoe UI Emoji',
               'Segoe UI Historic', 'Segoe UI Symbol', 'Shonar Bangla', 'Shruti', 'SimHei', 'SimKai',
               'Simplified Arabic', 'Simplified Chinese', 'SimSun', 'SimSun-ExtB', 'SimSun-ExtB', 'Sitka',
               'Snell Roundhan', 'Stencil Std', 'Sylfaen', 'Symbol', 'Tahoma', 'Thai', 'Times New Roman',
               'Traditional Arabic', 'Traditional Chinese', 'Trattatello', 'Trebuchet MS', 'Tunga',
               'UD Digi Kyokasho', 'UD Digi KyoKasho NK-R', 'UD Digi KyoKasho NK-R', 'UD Digi KyoKasho NP-R',
               'UD Digi KyoKasho NP-R', 'UD Digi KyoKasho N-R', 'UD Digi KyoKasho N-R', 'Urdu Typesetting',
               'URW Chancery', 'Utsaah', 'Vani', 'Verdana', 'Verdana Pro', 'Vijaya', 'Vrinda', 'Westminster',
               'Yu Gothic', 'Yu Gothic UI', 'Yu Mincho', 'Zapf Chancery']

# lorem ipsum
lorem = 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nam ultricies eget enim et interdum. Proin viverra,' \
        ' mi at vulputate imperdiet, lorem velit suscipit urna, id suscipit magna nibh ac ex. Morbi lorem neque,' \
        ' ultricies at ex ac, dictum pretium urna. Phasellus finibus fringilla tortor, id commodo dui tincidunt' \
        ' sit amet. Pellentesque ligula metus, convallis quis urna vitae, tempus consequat urna. Nulla eu est' \
        ' justo. Cras blandit quam sem, ut elementum lectus vehicula eu. Cras eget urna vel neque rutrum rhoncus. ' \
        'Nullam euismod tortor leo, non pretium mi tincidunt non. Cras nunc arcu, tincidunt sed lectus non, ' \
        'dapibus egestas metus. Fusce id dolor nec mi interdum ultrices a ut eros. Donec eget maximus velit, ' \
        'eget pretium urna.  Donec consequat sagittis felis. Nulla arcu nisl, sollicitudin non sagittis sit amet, ' \
        'vulputate vitae magna. Nam facilisis interdum vestibulum. Cras quis facilisis nisi, id interdum dui. ' \
        'Sed auctor cursus nibh vitae commodo. In fringilla scelerisque lorem, suscipit tincidunt ex vehicula ut. ' \
        'Mauris eget porta metus. Morbi sit amet nulla porttitor, interdum lorem et, vestibulum dolor. Sed dapibus, ' \
        'mauris et ornare rutrum, leo purus sollicitudin lorem, nec aliquam orci ex ac odio. Integer faucibus nunc quis ' \
        'feugiat cursus. Nam in bibendum dui, nec faucibus quam.  Donec non laoreet ex, non dignissim velit. ' \
        'Aenean condimentum risus nunc, in rutrum diam vehicula at. Vestibulum sodales ex ut est dictum, tempor ' \
        'luctus eros rutrum. In eu dui varius, hendrerit nisl vitae, lacinia justo. Donec facilisis urna tincidunt, ' \
        'porttitor erat sit amet, aliquam orci. Nullam nec ante quis magna vulputate scelerisque. Fusce sit amet' \
        ' malesuada purus, non sollicitudin tellus.  Quisque pellentesque risus sapien, vitae rhoncus magna' \
        ' tempus vitae. In suscipit viverra orci pharetra ultrices. Vivamus sit amet sollicitudin neque. ' \
        'Donec facilisis fringilla interdum. Vivamus nunc ipsum, bibendum at ornare quis, commodo eu libero. ' \
        'Nulla pulvinar, nisi at convallis iaculis, nunc purus commodo est, a laoreet tellus tortor non nisi. ' \
        'Donec dapibus tellus vel purus pellentesque, vel laoreet dolor finibus. Ut eget lectus cursus, ' \
        'scelerisque quam posuere, cursus lacus. Praesent et mi dolor. Nulla ultricies purus sem, a pulvinar ' \
        'ante mattis id. Quisque sed purus cursus, egestas eros eget, auctor arcu. Vestibulum sed tellus a ' \
        'nulla bibendum tincidunt at eget dolor. Praesent finibus ligula vel justo venenatis pretium.  ' \
        'Orci varius natoque penatibus et magnis dis parturient montes, nascetur ridiculus mus. ' \
        'Sed faucibus molestie faucibus. Fusce vel placerat nisi. Morbi lectus orci, dignissim nec lacus in, ' \
        'tincidunt maximus libero. Aenean convallis facilisis leo et ullamcorper. Fusce maximus et ' \
        'tortor vitae mollis. Etiam nec porta libero.  Nam posuere lacus turpis, eget hendrerit mauris rhoncus vel.' \
        ' Morbi mollis arcu eu mattis pellentesque. Integer efficitur pharetra urna et sollicitudin. ' \
        'Mauris pellentesque dictum mattis. Morbi dictum arcu et augue posuere, a pharetra ligula convallis. ' \
        'Sed tincidunt justo luctus, ornare risus aliquam, tristique sapien. Proin et efficitur elit,' \
        ' id blandit nisl.  Quisque ut nisl a lectus porta tincidunt. Phasellus rutrum massa nisi, a tristique' \
        ' turpis pretium sit amet. Sed quis tristique quam. Vivamus placerat placerat accumsan.' \
        ' Ut blandit sollicitudin auctor. Nam et nibh nisl. Mauris egestas ipsum vitae nisi aliquam,' \
        ' mollis varius tellus fringilla. Curabitur luctus pellentesque lorem, sed euismod metus vehicula' \
        ' ultricies. Maecenas dignissim semper diam id porttitor. Cras vitae felis auctor, vehicula leo id, ' \
        'ornare lacus. Nam interdum ipsum ac risus condimentum sodales. Nulla lacinia enim eu neque rhoncus ' \
        'eleifend. Pellentesque sollicitudin condimentum feugiat. Maecenas lacus nulla, auctor et rhoncus sed,' \
        ' imperdiet in ante. In sit amet consequat ante, in venenatis mi.'

# all backgrounds from the 'backgrounds' folder
backgrounds = []

for path in os.listdir("backgrounds"):
    full_path = "backgrounds/" + path
    backgrounds.append(os.path.abspath(full_path))
