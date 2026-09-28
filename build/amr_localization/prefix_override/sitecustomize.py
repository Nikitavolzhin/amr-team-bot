import sys
if sys.prefix == '/usr':
    sys.real_prefix = sys.prefix
    sys.prefix = sys.exec_prefix = '/home/ashraful/HBRS/AMR/AMR_PROJECT/amr-team-bot/install/amr_localization'
