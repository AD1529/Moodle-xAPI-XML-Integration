from pandas import DataFrame
import pandas as pd
import numpy as np


def add_activity_status(df: DataFrame) -> DataFrame:
    """
    Identify actions performed on deleted modules or deleted users

    Returns:
         two values: DELETED or Available.
    """

    df.loc[(df.Description.str.contains('deleted')), 'Status'] = 'DELETED'
    # df.loc[(df.Status == 'DELETED') & (df.Path.str.contains('attempt')), 'Status'] = 'Available'

    df.loc[df['Status'].isnull(), 'Status'] = 'Available'

    return df


def get_group_table(df: DataFrame, course: int) -> DataFrame:
    """
    Create a table with the assigned and unassigned groups based on the difference (assigned-unassigned)

    Parameters
    ----------
    df: dataframe
    course: course id

    Returns
    -------
    A table with assigned and unassigned groups

    """
    groups_125 = {
        'MAJ3 A': 'MAJ3 A',
        'MAJ3 B': 'MAJ3 B',
        'DM-PM A': 'DM-PM A',
        'DM-PM B': 'DM-PM B',
    }

    groups_153 = {
        'MonoEsca3': 'Géosciences et Escalade',
        'Monopat2': 'Patrimoine',
        'Monopat1': 'Patrimoine'
    }

    groups_313 = {
        '4cd427c2e6dbe30ad2a660ae4761f03afb00fe751258a9bad0ddbc010e80ccd0': 'CS Mono/MinST',
        '6fdf9665e78d0def5cda457066a1abd00cb86431402d08c6b4e2f871ff33beb1': 'TP Mono/MinST'
    }

    groups_1527 = {
        'SCNA21-1A': 'SCNA21-1A',
        'SCNA21-2A': 'SCNA21-2A',
        'SCNA21-3A': 'SCNA21-3A',
        'SCNA21-4A': 'SCNA21-4A',
        'SCNA21-5A': 'SCNA21-5A',
        'SCNA21-1B': 'SCNA21-1B',
        'SCNA21-2B': 'SCNA21-2B',
        'SCNA21-3B': 'SCNA21-3B',
        'SCNA21-4B': 'SCNA21-4B',
        'SCNA21-5B': 'SCNA21-5B',

        'SCNA22-1A': 'SCNA22-1A',
        'SCNA22-2A': 'SCNA22-2A',
        'SCNA22-3A': 'SCNA22-3A',
        'SCNA22-4A': 'SCNA22-4A',
        'SCNA22-1B': 'SCNA22-1B',
        'SCNA22-2B': 'SCNA22-2B',
        'SCNA22-3B': 'SCNA22-3B',
        'SCNA22-4B': 'SCNA22-4B',

        'SCNA23-1A': 'SCNA23-1A',
        'SCNA23-2A': 'SCNA23-2A',
        'SCNA23-3A': 'SCNA23-3A',
        'SCNA23-4A': 'SCNA23-4A',
        'SCNA23-1B': 'SCNA23-1B',
        'SCNA23-2B': 'SCNA23-2B',
        'SCNA23-3B': 'SCNA23-3B',
        'SCNA23-4B': 'SCNA23-4B',

        'SCNA24-1A': 'SCNA24-1A',
        'SCNA24-2A': 'SCNA24-2A',
        'SCNA24-3A': 'SCNA24-3A',
        'SCNA24-4A': 'SCNA24-4A',
        'SCNA24-5A': 'SCNA24-5A',
        'SCNA24-1B': 'SCNA24-1B',
        'SCNA24-2B': 'SCNA24-2B',
        'SCNA24-3B': 'SCNA24-3B',
        'SCNA24-4B': 'SCNA24-4B',
        'SCNA24-5B': 'SCNA24-5B',

        'PEIPB-1A': 'PEIPB-1A',
        'PEIPB-1B': 'PEIPB-1B',
        'DC1': 'DC1',
        'DC2': 'DC2',
        'SCH': 'SCH',
        'SPH': 'SPH',
        'SHI': 'SHI',
        'SA': 'SA',
        'Maj-M': 'Maj-M',
        'SDR': 'SDR',
        'SDE': 'SDE',
        'BIO MAD': 'BIO MAD',
        'SHSE-Tiers-temps': 'SHSE-Tiers-temps',
        'Accès restreint': 'Accès restreint',
        'DISP': 'DISP'
    }

    groups_1539 = {
        '58b2cb49e0086833e1c7b2a8714ebaf7470b170df7e67786642ceb2898a267f0': 'Groupe 4',
        'e247a49ede69c2e57264409e542db9c69220c5a68aa8dc2829f77ae08dc7d510': 'Groupe 5',
        '0b878edc5d4d87464120622ea2369947c42db3cc8b0c46c5ee407e8fca3f504d': 'Groupe 6',
        'ee66bf49e7caab10fe80ef17120ed2ebbbf16a8f3d1c570634d9c672fa3942ed': 'Rendu 7 - Groupe 00',
        'af42065c3400b59077be423925ab1a1398091a0b11ad930c8adb5d5f4b22b169': 'Rendu 7 - Groupe 01',
        '7c8556b029f41ab22e14ecfac1c57f8e94ad94f582142ce2092581958082b6ad': 'Rendu 7 - Groupe 02',
        '2eda0f2404673e0fc916effcabef0e9e2b0c4363d05a09ef3f69c92dff1f85c0': 'Rendu 7 - Groupe 03',
        '178959de9d58990eff7b925c2d8a9244386120af1707679bd60e5dd0b8b6225a': 'Rendu 7 - Groupe 04',
        '97dca49ba9b4813623e706a0743d944c7f6f2ca20eb32ca04998b48d08322115': 'Rendu 7 - Groupe 05',
        'a16e95f12e9c0cbb6125654f90d1e056fe28cc3da32a6ebed33757ab8112e243': 'Rendu 7 - Groupe 06',
        '7ab9d9badc76145903839c2bb2efd8ece76c9d48649e446c999ba1308ab845af': 'Rendu 7 - Groupe 07',
        '3a1cafb63cccb5bfa4320e9406890079cf343eb3fe42aa35646187c267235f2e': 'Rendu 7 - Groupe 08',
        '42d45dd014475ddf5dafd964f0da5a100afc101b4f464924b63999f5d651d0c6': 'Rendu 7 - Groupe 09',
        '77f2b4251223d788d299266ed4ea45982c75cf9a94e797ad82ab9b17919630dc': 'Rendu 7 - Groupe 10',
        'b88852cf5e0e027b77b752412b5606fb9e2edaf830b1fd0c9ca5bdbd62ed255a': 'Rendu 7 - Groupe 11',
        '76b1285d96879b84fbc85b442cff51895807171104e2c70f031dfc0013a40a40': 'Rendu 7 - Groupe 12',
        '8d2081ea676d6ffde0386d280f210f45da2faf633d6d0d16059c57dea29f558d': 'Rendu 7 - Groupe 13',
        'd68f86c8a2f4e8f2e47dd22e352d9d9be9c2277790b5411c4472e86a104b0f4a': 'Rendu 7 - Groupe 14',
        '991ea419fb23d7f732619b16adf309459436868016a2f5a8202d94654e8922e7': 'Rendu 7 - Groupe 15',
        '8ee8089b262bd8f4fca81d555c149d8cb52b4825960a1ca4b34201acce6faa58': 'Rendu 7 - Groupe 16',
        '6d3f81555f72bc79fea9c9a2bc9f90b045995e014762d950a7e748c4922aaa7f': 'Rendu 7 - Groupe 17',
        'd1b73dd80e0a5fa7be67c7683f049ed357c54a62c38609891d425e12960c8995': 'Rendu 7 - Groupe 18',
        '562ef545af888e4b6b8830f3d458f8f377c8b9331ea53fa37af34aac3696f3bb': 'Rendu 7 - Groupe 19',
        '237524099322b4fa2941eb84c1182f2a31f47b22edafa2388df8dbeb1bc1f019': 'Rendu 7 - Groupe 20',
        'df2ca84ffb152b99b4f4abe7a578bcf524670d26a93ee5b7b2e3ae19f1c51b48': 'Rendu 7 - Groupe 21',
        # '8065a91f5fcbc8b8073615485dd4756e57bb09d67c284dffb6b02721a5e7aeac': 'Rendu 7 - Groupe 22', # not in list
        '3fb7750f0c309b3aa2184b794397e8fe64230f9e1705538bab1e8448b102dfc0': 'Rendu 7 - Groupe 23',
        # '99ebf08f3724c06c4018b2e1e9f4a19678788c8125a814d9420033140b1d14b2': 'Rendu 7 - Groupe 24', # not in list
        # 'a1c6d81aa70b3e26de6025776794dc6f39bef708bb7316148e232cb783d550f8': 'Rendu 7 - Groupe 25', # not in list
        # '0cc4a6db3d35857cc45c117a532948528ed9da56c5e5fcadd0454d88e1e549d8': 'Rendu 7 - Groupe 26', # not in list
        # 'cbd2c1beb5e82987c1c0674c9c848c63879cf59ad0ca2a0490f4510ffacac110': 'Rendu 7 - Groupe 27', # not in list
        # '52c65f1842260cd9b749c2fed94b69da2f2f99bc371085364989f480a5586a19': 'Rendu 7 - Groupe 28', # not in list
        # 'be396da0cd0ef0e04f65abbaf6c96df2d6276bd8aca0dead0bea25cdded61e6c': 'Rendu 7 - Groupe 29', # not in list
        'b5f79e41beca468ec34d0af5915505cd60ee1daec5de789b07ad3b5c1a6298cf': 'Rendu 7 - Groupe 30',
        # '2d494eb51c37c8579abc782dbcdf4a2e7c9effe0892fc8ccfba574bf95f5212a': 'Rendu 7 - Groupe 31', # not in list
        # 'b4bec67ae62e280e91349a2a0582cecbf1bf961d5f642ca0add5283260947b8a': 'Rendu 7 - Groupe 32', # not in list
        '6559f753e4f054259ffc5627103591d1bb20bf65163b01f1bb307f2adcad1e89': 'Rendu 7 - Groupe 33',
        # '1c01c46189b8d8f7befe128d690def9ff09cb8aa00e1005e4c9aa3ab09097d51': 'Rendu 7 - Groupe 34', # not in list
        'dd08636426ac4c3a284d7e817a68813427330dae6912648b3ffaab371d5abf59': 'Rendu 7 - Groupe 35',
        '73817b06f55017e16a0e187135d8b9d7238e614afd67b60d833023865b3b7ddd': 'Rendu 9 - Groupe 00',
        'ab30e1011ebaa3fd6aa8b50eaa1ce5e4c290bd10358dff81370725a0d44378c1': 'Rendu 9 - Groupe 01',
        'd63b2c0bdff3f8cc4719113bfa33d8642895f6b9c08a6b8e36e868dc9d7178e9': 'Rendu 9 - Groupe 02',
        'e08dcc4d45fc5d0ca6fed72b2d0a82e42ca0437fabe4ee7779daaad0d58d35f4': 'Rendu 9 - Groupe 03',
        '7177d8e1568635077ab203c116fe5992f3e8c56bfe64d0b892ec8bd58503c64a': 'Rendu 9 - Groupe 04',
        '9217211d2d956324db2451b2132798f8612cdc0e48a1b42fdfad9e16ab3f158b': 'Rendu 9 - Groupe 05',
        '04e03662d8193dd112ae570b7b1c14de64cf893b62434321253522fd9928a329': 'Rendu 9 - Groupe 06',
        '04bc2ae792512901b8f0ee1c5abded7b8c3288f4e38d39c580457b0a6ff7de25': 'Rendu 9 - Groupe 07',
        '2d062fe7402c1836c57124d50cbffda6a96db12ae4ffe8559bd261bd10ac57f5': 'Rendu 9 - Groupe 08',
        'bcf11a866ebc11dd09a0d9a068db1d21697cdfc5c5b0f904852b84736f40485e': 'Rendu 9 - Groupe 09',
        '2a597c5131a2ea8e1cea2b2d264e526203bd735a8d8bc3b3efec3b894da23617': 'Rendu 9 - Groupe 10',
        '0638aba7dfbd74b458b99c4b2fc95a866015cb7ca795c0c74ca0d319e61e5808': 'Rendu 9 - Groupe 11',
        'ecfd9be6d3d0554e7d9dca0cb3e8d4d1bbec8d8b67029cf846c6a7618fcb376e': 'Rendu 9 - Groupe 12',
        '29f0d64d68164db10262a92b627c6146647b2a259c063a725988453fe5ee3b05': 'Rendu 9 - Groupe 13',
        '0026944a800e139e2f9ad56d56fbe9212c363a97fac24e7aaa3b9c8620627bdd': 'Rendu 9 - Groupe 14',
        'ed3b04bf02aa30f0bf514032703c3b07d62ed0fdc1f5c0dccebc20be4e003ae2': 'Rendu 9 - Groupe 15',
        '06d7bd033581be215770b541e27b48443d29de4365e553e79d4c8678e1a736b6': 'Rendu 9 - Groupe 16',
        '887f348eea176bb1be89cc7babf84b5e7d40a07bd40b7dd38b671b6c7e6103f5': 'Rendu 9 - Groupe 17',
        # 'e7dda0b1ab6e4a11ef6032d7388426d7239ec4f39852bbb2d0188ee41f5b0f33': 'Rendu 9 - Groupe 18', # not in list
        'a484e6cee2df70cc93e61ab0da8b9c7eac7e286eb63a9e9b379769a518cfcc42': 'Rendu 9 - Groupe 19',
        '429afa70df30b2133e351c3dcdce2e94b80f5397dbb98869371d19f84d210dce': 'Rendu 9 - Groupe 20',
        '29795030a08a3fd0d4f432aac43097ae6b406a09debed6c9b014bd03cfdf3f83': 'Rendu 9 - Groupe 21',
        # '5e971abb13ce8560a931e8adaf1b0acb93cf9ec6c5c06fa33192016f53d91863': 'Rendu 9 - Groupe 22', # not in list
        '54f42c4889bcfe1300b7032ad6db379f8dd84323e8f426bebc16b7d233a9763a': 'Rendu 9 - Groupe 23',
        # '734bfdb7372ffcd3ff75ac8ff39917bde3c6ca2191bb79d13cb227b08eac5b66': 'Rendu 9 - Groupe 24', # not in list
        '48acfd914f73f18435217cf9d6c3528c3d3064b872ae8e4375d21575914816c2': 'Rendu 9 - Groupe 25',
        # '907fceae1c268ec34db039f4b7831962e797a2d633750fd1e3e97d43b03cc556': 'Rendu 9 - Groupe 26', # not in list
        # '620383ae18f48be256e4e66e1eff9ea82f7da157c252a4e3cc3bf98f328c5eb6': 'Rendu 9 - Groupe 27', # not in list
        # '45fdf028397fd99c9136d3560442140dd0d8bfc520062774a22307e7bacfdb1d': 'Rendu 9 - Groupe 28', # not in list
        # '53ca65f5fa21abd6e48bf546ea162a672b607e47ffb9a375bf1da99777fb6df2': 'Rendu 9 - Groupe 29', # not in list
        'a7485c73d6ec433d7a3bd30d8a0a2a52bbe0831da62d3fddc120468df0027e20': 'Rendu 9 - Groupe 30',
        # '0f0c3e9da35122560298b7982ab2a0a01c17ca95986a67994daead84f4bf1abd': 'Rendu 9 - Groupe 31', # not in list
        '60d62e1eff5c36e667ab2eb2b75d212f9fc59a8e6749e6b722e26e7a1cd782a8': 'Rendu 9 - Groupe 32',
        # '3a3eb31d779e0737f6afa09e755ede1190d9a554845f1c0074298975ad76683b': 'Rendu 9 - Groupe 33', # not in list
        # 'aa4c739220b9e2436fdbbb3a1bb2f02eba112e3ee77f982c4e9ea6f0e449fd3f': 'Rendu 9 - Groupe 34', # not in list
        '8169087f6455872888380f899d6cb2b96c98d7482548fbc4da0271f717257f58': 'Rendu 9 - Groupe 35',
        '255b19357b15f6dbb02eb9fd5f4e96e3677fdebd9ff46da410d6199f4d63fdc7': 'Rendu-00',
        '2370786a47f72aecd0959b86e9c0c638bcff958c6c3d5a38373e5f3de2f13695': 'Rendu-01',
        '0f6034bad6ce0c6c9c75a6af45c5b95505e993642556b7a4d81725c5d835b953': 'Rendu-02',
        '782c3af49a24b1e88739497528640894fa46414b32bd463e9f5bd90f5c4b5a6f': 'Rendu-03',
        '95052a4a20e2ef62f09c8c7ceb3380cd4ad7b8cf425249a5a95451dd9ef4a1e1': 'Rendu-04',
        'bd3f2c067019bd49cfef90ff5ed951c6f19b65373521a26bdf2cec6b54870838': 'Rendu-05',
        'de14ac5a528c3e0b992ce35b6f38ddd43d1acd65f4fb95e813fde71b0cd4cb14': 'Rendu-06',
        'aa05fdc4c3b9e6798b2e91ac873ebaf1039898f31b6158f6a2cd24046418b2ae': 'Rendu-07',
        '59c3584fd3faf70676a63f9cafcffa82eb0b886bfc557eda0e8abafab26f36a5': 'Rendu-08',
        '947d74030f0f292fd502456835fc524e062a59470ee3007126660e2ffe12a589': 'Rendu-09',
        'c5071c3a9b84ebe3a35bf9cf8c97b6cbe688884e7a364de51f29ca1f9ec4f2a7': 'Rendu-10',
        '9bf71b441f3e4770c79018bf186629d8257f5178da6a582a35f4d6f53d6dee70': 'Rendu-11',
        '3015467de8af7b5b77e614f319bad52cb0c736397fa42e4e3531943dfa501225': 'Rendu-12',
        '819cbd82cbed6e579d8155334d34ad1110b3c7c33b7ee9c05ea0b2d7e4ccceba': 'Rendu-13',
        'e4ce38f540d58ae72c38f252d903ff9eeb2850a2ac3df26a56cf4bc383113466': 'Rendu-14',
        '5207592236096ba510aa71e1a99160853f0b4fbe90c679c2f5ba9b8906880e62': 'Rendu-15',
        '35135b04fddb39d398780280d6140710173f0d8375489c50785b7badff93f95d': 'Rendu-16',
        'a8eacd049bf6910c3f5475b1db266707429745889e1a5d8d313748979574d9a4': 'Rendu-17',
        'dc3d0e37d538da64609cfcdf16014146b38d0c03a5d2ff991cc4fb6f03699f21': 'Rendu-18',
        'db002b493b46c46ad425a38026cbe2dcd80a703496ed1e38dca25bbaaf1f389b': 'Rendu-19',
        '3e75aa98a556e15fa57f6444dbc775d3eb5f46002bc3d6e8fd1b272c97c8d511': 'Rendu-20',
        '8b4639c93536e62c3b0941223760568f0f2c4aad4a87a69dbbb03fdb46ec69fc': 'Rendu-21',
        'f68a69dc490503ecbe24a49a9b68cea97157b7b1167763ed90aec1947892d903': 'Rendu-22',
        '54febe7ccc0bba03b47eeda3eebe2a9827d027bd9d6b7742f57d927f9c1858d1': 'Rendu-23',
        '47c8b5380ead68aec32be46260cd8911c66c6716ff04842bb806c69b71d479f9': 'Rendu-24',
        '1a6b77dc4f121e4c73c48cb020afeeca4e7b521b245ca0090745f8d833caeeef': 'Rendu-25',
        '6268edb87a6a46eca68406107de7667432a47ad25e5de41440e45c31c07a122a': 'Rendu-26',
        '0ecb580f1cdab9825268a6f17cb8d80dea26625329ab9ddf4e6fcdadd3c63106': 'Rendu-27',
        '5dc7f2b2e71dc27658b3e5dad4323124074e463bed530f261ef516f82614e7c0': 'Rendu-28',
        'ff89bff8ea16f3322d10d1a0f4c01ee4c43b16a58233a4dcb19f98eff1114ec6': 'Rendu-29',
        # '0bb947536a0878497881059a7249a52852ad6fb1a6f96a6b59e65bcfe072c52d': 'Rendu-30', # not in list
        # '58f32cc8560d15a7b15659b1a0caaf3482c95777c7dfef707e8d9c841cad3692': 'Rendu-31', # not in list
        # '7cbb750e61f69b7cac95b849b59d8aa8f8c52d08aff50713c32c8e7e07ace54f': 'Rendu-32', # not in list
        # '14ae5551ecf26225698b70d0799a092c40bf14e1dbaf4c60ac0197b0b420a5b0': 'Rendu-33', # not in list
        # '8a86a8b765d449bd6bf497163d762aabdf3cd13657c61975d1bba6fe1a4ca887': 'Rendu-34', # not in list
        # 'ab77f965b2a14098c0ffe81b69ad5bba25468ade8c0248db6fc6d3fe39a2fe90': 'Rendu-35' # not in list
    }

    groups_1587 = {
        'DC1-A': 'DC1-A',
        'DC1-B': 'DC1-B',
        'DC2-A': 'DC2-A',
        'DC2-B': 'DC2-B',
        'DISPENSE': 'DISPENSE',
        'L0-3A': 'L0-3A',
        'L0-3B': 'L0-3B',
        'PEIPB-A': 'PEIPB-A',
        'PEIPB-B': 'PEIPB-B',
        'SA': 'SA',
        'SCH': 'SCH',
        'SCNA11-1A': 'SCNA11-1A',
        'SCNA11-1B': 'SCNA11-1B',
        'SCNA11-2A': 'SCNA11-2A',
        'SCNA11-2B': 'SCNA11-2B',
        'SCNA11-3A': 'SCNA11-3A',
        'SCNA11-3B': 'SCNA11-3B',
        'SCNA11-4A': 'SCNA11-4A',
        'SCNA11-4B': 'SCNA11-4B',
        'SCNA12-1A': 'SCNA12-1A',
        'SCNA12-1B': 'SCNA12-1B',
        'SCNA12-2A': 'SCNA12-2A',
        'SCNA12-2B': 'SCNA12-2B',
        'SCNA12-3A': 'SCNA12-3A',
        'SCNA12-3B': 'SCNA12-3B',
        'SCNA12-4A': 'SCNA12-4A',
        'SCNA12-4B': 'SCNA12-4B',
        'SCNA12-5A': 'SCNA12-5A',
        'SCNA12-5B': 'SCNA12-5B',
        'SCNA13-1A': 'SCNA13-1A',
        'SCNA13-1B': 'SCNA13-1B',
        'SCNA13-2A': 'SCNA13-2A',
        'SCNA13-2B': 'SCNA13-2B',
        'SCNA13-3A': 'SCNA13-3A',
        'SCNA13-3B': 'SCNA13-3B',
        'SCNA13-4A': 'SCNA13-4A',
        'SCNA13-4B': 'SCNA13-4B',
        'SCNA13-5A': 'SCNA13-5A',
        'SCNA13-5B': 'SCNA13-5B',
        'SCNA14-1A': 'SCNA14-1A',
        'SCNA14-1B': 'SCNA14-1B',
        'SCNA14-2A': 'SCNA14-2A',
        'SCNA14-2B': 'SCNA14-2B',
        'SCNA14-3A': 'SCNA14-3A',
        'SCNA14-3B': 'SCNA14-3B',
        'SCNA14-4A': 'SCNA14-4A',
        'SCNA14-4B': 'SCNA14-4B',
        'SCNA14-5A': 'SCNA14-5A',
        'SCNA14-5B': 'SCNA14-5B',
        'SDE': 'SDE',
        'SDR': 'SDR',
        'SHI': 'SHI',
        'SPH': 'SPH'
    }

    groups_2781 = {
        # 'A': 'A',
        'A1a': 'A1a',
        'A1b': 'A1b',
        'A2a': 'A2a',
        'A2b': 'A2b',
        'A3a': 'A3a',
        'A3b': 'A3b',
        'A4a': 'A4a',
        'A4b': 'A4b',
        'A5a': 'A5a',
        'A5b': 'A5b',
        'A6a': 'A6a',
        'A6b': 'A6b',
        # 'B': 'B',
        'B1a': 'B1a',
        'B1b': 'B1b',
        'B2a': 'B2a',
        'B2b': 'B2b',
        'B3a': 'B3a',
        'B3b': 'B3b',
        'B4a': 'B4a',
        'B4b': 'B4b',
        'B5a': 'B5a',
        'B5b': 'B5b',
        'B6a': 'B6a',
        'B6b': 'B6b',
        # 'C': 'C',
        'C1a': 'C1a',
        'C1b': 'C1b',
        'C3a': 'C3a',
        'C3b': 'C3b',
        'C4a': 'C4a',
        'C4b': 'C4b',
        'C5a': 'C5a',
        'C5b': 'C5b',
        'C6a': 'C6a',
        'C6b': 'C6b',
        # 'D': 'D',
        'D1a': 'D1a',
        'D1b': 'D1b',
        'D3a': 'D3a',
        'D3b': 'D3b',
        'D4a': 'D4a',
        'D4b': 'D4b',
        'D5a': 'D5a',
        'D5b': 'D5b',
        'D6a': 'D6a',
        'D6b': 'D6b',
        # 'E': 'E',
        'E1a': 'E1a'
    }

    groups_3135 = {
        'dac1e8109ea53aaaf71636df133d3f57ab6f9d91781840d5aafa81a9bcbe8287': 'Groupe 1',
        '5e811d81a4ed934ec593855a5ecf1b0eab1f21a86ece7e1ea5f6745912552147': 'Groupe 2',
        '19c0cc3ee299cc1cdf8f107ce0d55d21ad8683f3964b0dbb822ec9ac5519b818': 'Groupe 3',
        '58b2cb49e0086833e1c7b2a8714ebaf7470b170df7e67786642ceb2898a267f0': 'Groupe 4',
        'e247a49ede69c2e57264409e542db9c69220c5a68aa8dc2829f77ae08dc7d510': 'Groupe 5',
        '0b878edc5d4d87464120622ea2369947c42db3cc8b0c46c5ee407e8fca3f504d': 'Groupe 6',
        '6788c2a22fcd2a716ba744f9c774c7d8f8ee92de1312113a915d326d87cc4e1c': 'Groupe 7',
        'b98bb141c31363fa3d0e7a2fbeb0840301fa8f606c1dfee537df7e0a094c0f94': 'Groupe 8',
    }

    groups_3499 = {
        'ABUDHABI-P': 'ABUDHABI-P',
        'CMI-E': 'CMI-E',
        'CMI-M-A': 'CMI-M-A',
        'CMI-M-B': 'CMI-M-B',
        'CMI-P-A': 'CMI-P-A',
        'CMI-P-B': 'CMI-P-B',
        'DC1-A': 'DC1-A',
        'DC1-B': 'DC1-B',
        'DC1_TD': 'DC1-TD',
        'DC1_TP': 'DC1-TP',
        'DC2': 'DC2',
        'DC3': 'DC3',
        'DC_SA': 'DC-SA',
        'DC_SDE': 'DC-SDE',
        'DC_SDR': 'DC-SDR',
        'DC_SHI': 'DC-SHI',
        'DC_SMU': 'DC-SMU',
        'EAD': 'EAD',
        'EADSCFO-G1': 'EADSCFO-G1',
        'EADSCFO-G2': 'EADSCFO-G2',
        'EADSCFO-G3': 'EADSCFO-G3',
        'EADSCFO-G4': 'EADSCFO-G4',
        'EADSCFO-G5': 'EADSCFO-G5',
        'EADSCIN-G1': 'EADSCIN-G1',
        'EADSCIN-G2': 'EADSCIN-G2',
        'EADSCIN-G3': 'EADSCIN-G3',
        'EADSCIN-G4': 'EADSCIN-G4',
        'EADSCMA-G1': 'EADSCMA-G1',
        'EADSCMA-G2': 'EADSCMA-G2',
        'EADSCMA-G3': 'EADSCMA-G3',
        'EADSCMA-G4': 'EADSCMA-G4',
        'PEIPA-1A': 'PEIPA-1A',
        'PEIPA-1B': 'PEIPA-1B',
        'PEIPA-2A': 'PEIPA-2A',
        'PEIPA-2B': 'PEIPA-2B',
        'PEIPA-3A': 'PEIPA-3A',
        'PEIPA-4A': 'PEIPA-4A',
        'PEIPA-4B': 'PEIPA-4B',
        'PEIPA-5A': 'PEIPA-5A',
        'PEIPA-5B': 'PEIPA-5B',
        'SCFO22-6A': 'SCFO22-6A',
        'SCFO22-6B': 'SCFO22-6B',
        'SCFO23-1A': 'SCFO23-1A',
        'SCFO23-1B': 'SCFO23-1B',
        'SCFO23-2A': 'SCFO23-2A',
        'SCFO23-2B': 'SCFO23-2B',
        'SCFO23-3A': 'SCFO23-3A',
        'SCFO23-3B': 'SCFO23-3B',
        'SCFO23-4A': 'SCFO23-4A',
        'SCFO23-4B': 'SCFO23-4B',
        'SCFO23-5A': 'SCFO23-5A',
        'SCFO23-5B': 'SCFO23-5B',
        'SCFO23-6A': 'SCFO23-6A',
        'SCFO23-6B': 'SCFO23-6B',
        'SCFO23-7A': 'SCFO23-7A',
        'SCFO23-7B': 'SCFO23-7B',
        'SCIN-1A': 'SCIN-1A',
        'SCIN-1B': 'SCIN-1B',
        'SCIN-2A': 'SCIN-2A',
        'SCIN-2B': 'SCIN-2B',
        'SCIN-3A': 'SCIN-3A',
        'SCIN-5A': 'SCIN-5A',
        'SCIN-5B': 'SCIN-5B',
        'SCIN-6A': 'SCIN-6A',
        'SCIN-7A': 'SCIN-7A',
        'SCIN-7B': 'SCIN-7B',
        'SCMA21-2A': 'SCMA21-2A',
        'SCMA21-2B': 'SCMA21-2B',
        'SCMA21-3A': 'SCMA21-3A',
        'SCMA21-3B': 'SCMA21-3B',
        'SCMA21-4A': 'SCMA21-4A',
        'SCMA21-4B': 'SCMA21-4B',
        'SCMA22-1A': 'SCMA22-1A',
        'SCMA22-1B': 'SCMA22-1B',
        'SCMA22-2A': 'SCMA22-2A',
        'SCMA22-2B': 'SCMA22-2B',
        'SCMA22-3A': 'SCMA22-3A',
        'SCMA22-3B': 'SCMA22-3B',
        'SCMA23-1A': 'SCMA23-1A',
        'SCMA23-1B': 'SCMA23-1B',
        'SCMA23-2A': 'SCMA23-2A',
        'SCMA23-2B': 'SCMA23-2B',
        'SCMA23-3A': 'SCMA23-3A',
        'SCMA23-3B': 'SCMA23-3B',
        'SCMA23-4A': 'SCMA23-4A',
        'SCMA23-4B': 'SCMA23-4B',
        'SCMA23-5A': 'SCMA23-5A',
        'SCMA23-5B': 'SCMA23-5B',
        'SPH': 'SPH',
        'SPRINT': 'SPRINT',
        'Tutorat_Bradai': 'Tutorat_Bradai',
        'Tutorat_Malanda': 'Tutorat_Malanda',
        'Tutorat_Nepaul': 'Tutorat_Nepaul'
    }

    groups_3559 = {'SPRINT A': 'SPRINT A',
                   'SPRINT B': 'SPRINT B',
                   'MONO1 A': 'MONO1 A',
                   'MONO1 B': 'MONO1 B',
                   'MONO2 A': 'MONO2 A',
                   'MONO2 B': 'MONO2 B',
                   'MONO3 A': 'MONO3 A',
                   'MONO3 B': 'MONO3 B',
                   'PAD': 'PAD'}

    groups_3789 = {
        'groupe 1': 'Groupe 1',
        'groupe 2': 'Groupe 2',
        'groupe 3': 'Groupe 3'
    }

    # correspondence course - groups list
    course_groups = {
        125: groups_125,
        # 141: no real groups, one person per group
        153: groups_153,
        313: groups_313,
        1527: groups_1527,
        1539: groups_1539,  # TODO
        1587: groups_1587,
        2781: groups_2781,
        # 2961: no groups
        3135: groups_3135,
        3499: groups_3499,
        3559: groups_3559,
        3789: groups_3789,
        # 3791: no groups
    }

    if course in course_groups.keys():

        group_list = course_groups[course]

        # users that have been added in a group
        added = df.loc[(df.CourseID == course)
                       & (df.Component == 'Groups')
                       & (df.Event_name == 'Group member added')][['User', 'Context']]
        added['Group'] = added['Context'].map(group_list)

        # users that have been removed from a group
        removed = df.loc[(df.CourseID == course)
                         & (df.Component == 'Groups')
                         & (df.Event_name == 'Group member removed')][['User', 'Context']]
        removed['Group'] = removed['Context'].map(group_list)

        # create a table to host the users with their corresponding group
        cols = ['User'] + list(set(group_list.values()))

        group_table = pd.DataFrame(columns=cols)
        group_table['User'] = added['User'].unique()
        group_table = group_table.mask(group_table.isna(), 0)  # fill the dataframe with 0 for the sum

        # fill the table with the assigned group
        for user in added['User'].unique():
            groups = added.loc[added['User'] == user]['Group'].values
            groups = [x for x in groups if str(x) != 'nan']
            for group in groups:
                group_table.loc[(group_table['User'] == user), group] = group_table.loc[
                                                                            (group_table['User'] == user), group] + 1

        # remove the unassigned group from the table
        for user in removed['User'].unique():
            groups = removed.loc[removed['User'] == user]['Group'].values
            groups = [x for x in groups if str(x) != 'nan']
            for group in groups:
                group_table.loc[(group_table['User'] == user), group] = group_table.loc[
                                                                            (group_table['User'] == user), group] - 1

        # fix double group assignment
        group_table[group_table == 2] = 1

    else:
        group_table = pd.DataFrame()

    return group_table


def assign_groups(group_table: DataFrame, df: DataFrame, course: int) -> DataFrame:
    """
    Assign the retrieved groups to the users in the dataframe

    Parameters
    ----------
    group_table: table with the groups for each user
    df: dataframe containing the users
    course: course ID

    Returns
    -------
    The dataframe with the field Group

    """

    df['Group'] = np.empty((len(df), 0)).tolist()

    if group_table.empty:
        df['Group'] = np.nan
    else:
        # remove all users that aren't added to a group
        group_table = group_table.loc[group_table[group_table.columns.difference(['User'])].sum(axis=1) != 0]

        for user in group_table.User:
            selected_user = group_table.loc[group_table.User == user]
            # a user can be added in more than one group
            group = selected_user.columns[(selected_user == 1).any()]
            # assign the groups to the user in the course
            df.loc[(df.User == user) & (df.CourseID == course), 'Group'] = \
                df.loc[(df.User == user) & (df.CourseID == course)]['Group'].apply(lambda x: list(group))
            # idxs = df.loc[(df.User == user) & (df.CourseID == course)].index
            # for idx in idxs:
            #     df.at[idx, 'Group'] = list(group)
            #     #test['b'] = test['b'].apply(lambda x: [5, 6, 7])

        # df.loc[(df.Group == np.str_('nan')), 'Group'] = np.nan

    return df


def integrate_icap_framework(df: DataFrame) -> DataFrame:
    # Course
    df.loc[df.Component == 'Course', 'ICAP'] = 'Passive'

    # assignment
    assignment = (df['Component'] == 'Assignment')
    df.loc[assignment & ((df['Event_name'] == 'Submission viewed') |
                         (df['Event_name'] == 'Feedback viewed') |
                         (df['Event_name'] == 'Course module instance list viewed') |
                         (df['Event_name'] == 'The submission has been graded')
                         ), 'ICAP'] = 'Passive'
    df.loc[assignment & ((df['Event_name'] == 'A submission has been submitted') |
                         (df['Event_name'] == 'Submission confirmation form viewed') |
                         (df['Event_name'] == 'Submission form viewed') |
                         (df['Event_name'] == 'The status of the submission has been viewed') |
                         (df['Event_name'] == 'The user duplicated their submission') |
                         (df['Event_name'] == 'Submission removed') |
                         (df['Event_name'] == 'A file has been uploaded') |
                         (df['Event_name'] == 'Submission created') |
                         (df['Event_name'] == 'Submission updated') |
                         (df['Event_name'] == 'An online text has been uploaded') |
                         (df['Event_name'] == 'Comment created') |
                         (df['Event_name'] == 'Comment deleted') |
                         (df['Event_name'] == 'Remove submission confirmation viewed')
                         ), 'ICAP'] = 'Constructive'

    # attendance
    df.loc[(df['Component'] == 'Attendance'), 'ICAP'] = 'Passive'

    # bigbluebutton
    df.loc[(df['Component'] == 'BigBlueButton'), 'ICAP'] = 'Passive'

    # book
    df.loc[(df['Component'] == 'Book'), 'ICAP'] = 'Passive'

    # chat
    chat = (df['Component'] == 'Chat')
    df.loc[chat & (df['Event_name'] == 'Sessions viewed'), 'ICAP'] = 'Passive'
    df.loc[chat & (df['Event_name'] == 'Message sent'), 'Event_name'] = 'Interactive'

    # checklist
    df.loc[df['Component'] == 'Checklist', 'ICAP'] = 'Active'

    # choice
    df.loc[df['Component'] == 'Choice', 'ICAP'] = 'Active'

    # database
    df.loc[df['Component'] == 'Database', 'ICAP'] = 'Constructive'

    # feedback
    df.loc[df['Component'] == 'Feedback', 'ICAP'] = 'Active'

    # folder
    df.loc[df['Component'] == 'Folder', 'ICAP'] = 'Passive'

    # forum
    forum = (df['Component'] == 'Forum')
    df.loc[forum & ((df['Event_name'] == 'Course searched') |
                    (df['Event_name'] == 'Discussion subscription created') |
                    (df['Event_name'] == 'Discussion subscription deleted') |
                    (df['Event_name'] == 'Discussion viewed') |
                    (df['Event_name'] == 'Read tracking disabled') |
                    (df['Event_name'] == 'Read tracking enabled') |
                    (df['Event_name'] == 'Subscription created') |
                    (df['Event_name'] == 'Subscription deleted') |
                    (df['Event_name'] == 'User report viewed')
                    ), 'ICAP'] = 'Passive'
    df.loc[forum & ((df['Event_name'] == 'Some content has been posted') |
                    (df['Event_name'] == 'Discussion created') |
                    (df['Event_name'] == 'Discussion deleted') |
                    (df['Event_name'] == 'Post created') |
                    (df['Event_name'] == 'Post deleted') |
                    (df['Event_name'] == 'Post updated')
                    ), 'ICAP'] = 'Interactive'

    # glossary
    df.loc[df['Component'] == 'Glossary', 'ICAP'] = 'Constructive'

    # group choice
    df.loc[df['Component'] == 'Group choice', 'ICAP'] = 'Active'

    # h5p
    h5p = (df.Component == 'H5P')
    df.loc[h5p & (df['Event_name'] == 'Report viewed'), 'ICAP'] = 'Passive'
    df.loc[h5p & (df['Event_name'] == 'xAPI statement received'), 'ICAP'] = 'Active'

    # lesson
    lesson = (df['Component'] == 'Lesson')
    df.loc[lesson & ((df['Event_name'] == 'Content page viewed') |
                     (df['Event_name'] == 'Lesson ended') |
                     (df['Event_name'] == 'Lesson restarted') |
                     (df['Event_name'] == 'Lesson resumed') |
                     (df['Event_name'] == 'Lesson started')
                     ), 'ICAP'] = 'Passive'
    df.loc[lesson & ((df['Event_name'] == 'Question answered') |
                     (df['Event_name'] == 'Question viewed')
                     ), 'ICAP'] = 'Active'

    # questionnaire
    questionnaire = (df['Component'] == 'Questionnaire')
    df.loc[questionnaire & ((df['Event_name'] == 'Attempt resumed') |
                            (df['Event_name'] == 'Responses saved') |
                            (df['Event_name'] == 'Responses submitted') |
                            (df['Event_name'] == 'Individual Responses report viewed')
                            ), 'ICAP'] = 'Active'
    df.loc[questionnaire & (df['Event_name'] == 'All Responses report viewed'), 'ICAP'] = 'Passive'

    # quiz
    quiz = (df['Component'] == 'Quiz')
    df.loc[quiz & ((df['Event_name'] == 'Quiz attempt abandoned') |
                   (df['Event_name'] == 'Quiz attempt started') |
                   (df['Event_name'] == 'Quiz attempt submitted') |
                   (df['Event_name'] == 'Quiz attempt summary viewed') |
                   (df['Event_name'] == 'Quiz attempt viewed') |
                   (df['Event_name'] == 'Quiz attempt reviewed')
                   ), 'ICAP'] = 'Active'

    # recent activity
    df.loc[df['Component'] == 'Recent activity', 'ICAP'] = 'Passive'

    # scheduler
    df.loc[df['Component'] == 'Scheduler', 'ICAP'] = 'Passive'

    # scorm
    df.loc[df['Component'] == 'SCORM package', 'ICAP'] = 'Active'

    # survey
    df.loc[df['Event_name'] == 'Survey response submitted', 'ICAP'] = 'Active'

    # wiki
    wiki = (df['Component'] == 'Wiki')
    df.loc[wiki & ((df['Event_name'] == 'Comments viewed') |
                   (df['Event_name'] == 'Wiki diff viewed') |
                   (df['Event_name'] == 'Wiki history viewed') |
                   (df['Event_name'] == 'Wiki page map viewed') |
                   (df['Event_name'] == 'Wiki page version viewed') |
                   (df['Event_name'] == 'Wiki page viewed')
                   ), 'ICAP'] = 'Passive'
    df.loc[wiki & ((df['Event_name'] == 'Comment created') |
                   (df['Event_name'] == 'Comment deleted') |
                   (df['Event_name'] == 'Wiki page created') |
                   (df['Event_name'] == 'Wiki page deleted') |
                   (df['Event_name'] == 'Wiki page updated') |
                   (df['Event_name'] == 'Wiki page version deleted') |
                   (df['Event_name'] == 'Wiki page version restored')
                   ), 'ICAP'] = 'Constructive'

    # workshop
    workshop = (df['Component'] == 'Workshop')
    df.loc[workshop & ((df['Event_name'] == 'A submission has been uploaded') |
                       (df['Event_name'] == 'Submission assessed') |
                       (df['Event_name'] == 'Submission created') |
                       (df['Event_name'] == 'Submission deleted') |
                       (df['Event_name'] == 'Submission re-assessed') |
                       (df['Event_name'] == 'Submission updated')
                       ), 'ICAP'] = 'Interactive'
    df.loc[workshop & (df['Event_name'] == 'Submission viewed'), 'ICAP'] = 'Passive'

    # user report
    grades = (df['Component'] == 'Grades')
    df.loc[grades & ((df['Event_name'] == 'Grade user report viewed') |
                     (df['Event_name'] == 'Course user report viewed')
                     ), 'ICAP'] = 'Passive'

    # user profile
    df.loc[df['Component'] == 'User profile', 'ICAP'] = 'Passive'

    # all components
    df.loc[df.Event_name == 'Course module viewed', 'ICAP'] = 'Passive'
    df.loc[df.Event_name == 'Course module instance list viewed', 'ICAP'] = 'Passive'

    # df.loc[df.ICAP.isnull(), 'ICAP'] = ''

    return df
