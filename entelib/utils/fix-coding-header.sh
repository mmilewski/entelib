# changes headers containing coding definition to format:
#       # -*- coding: utf-8 -*-
perl -i -pe 's@^(.*)\Q-*-\E(.*)coding(.*)utf(.*)\Q-*-\E@# -*- coding: utf-8 -*-@' `find ../ -iname '*.py'`
