import re
from pprint import pprint
from sqlite3 import dbapi2 as sqlite
from baseapp.models import *
from entelib.dbfiller import add_users
from datetime import datetime, date, timedelta


db_path = '/home/brzoska/entelib/entelib/migration/library.sqlite'
connection = sqlite.connect(db_path)
cursor = connection.cursor()


# retriving everything from old database
cursor.execute('SELECT * FROM users')
old_users = cursor.fetchall()
cursor.execute('SELECT * FROM events')
old_events = cursor.fetchall()
cursor.execute('SELECT * FROM books')
old_books = cursor.fetchall()

description_to_tuple = lambda e0: re.compile(r"(?:location|localization):?,? *(.*)\r\rcc:? ?(.*)\r\rcontact:? *(.*)", re.I).match(e0.replace('\n','\r')).groups()
# takes books.description
# returns tuple:
#   (location name, cost center, contact)

def normalize_location(name):
    separator = ';'
    bema = 'Bema Plaza'
    wpb = 'WPB, Strzegomska %s' + separator + 'room: %s'

    mapper = {u'Bema Plaza'                         : bema + separator + '%s floor, section %s' % ( '4-th', 'C'),
              u'Bema Plaza sekcja 4A'               : bema + separator + '%s floor, section %s' % ( '4-th', 'A'),
              u'Bema Plaza, 3-rd floor, section B'  : bema + separator + '%s floor, section %s' % ( '3-rd', 'B'),
              u'Bema Plaza, 3-th floor section B\t' : bema + separator + '%s floor, section %s' % ( '3-rd', 'B'),
              u'Bema Plaza, 4-th floor section A'   : bema + separator + '%s floor, section %s' % ( '4-th', 'A'),
              u'Bema Plaza, 4-th floor, section A'  : bema + separator + '%s floor, section %s' % ( '4-th', 'A'),
              u'Bema Plaza, 4-th floor, section B'  : bema + separator + '%s floor, section %s' % ( '4-th', 'B'),
              u'Bema Plaza, 4rd floor, section C'   : bema + separator + '%s floor, section %s' % ( '4-th', 'C'),
              u'Bema Plaza, 4th floor sectionC'     : bema + separator + '%s floor, section %s' % ( '4-th', 'C'),
              u'Bema Plaza, 4th floor, section A'   : bema + separator + '%s floor, section %s' % ( '4-th', 'A'),
              u'Bema Plaza, 4th floor, section B'   : bema + separator + '%s floor, section %s' % ( '4-th', 'B'),
              u'Bema Plaza, 4th floor, section C'   : bema + separator + '%s floor, section %s' % ( '4-th', 'C'),
              u'Bema, 3rd floor, section B'         : bema + separator + '%s floor, section %s' % ( '3-rd', 'B'),
              u'Bema, 4th floor, section B'         : bema + separator + '%s floor, section %s' % ( '4-th', 'B'),
              u'bema Plaza, 4th floor, section C'   : bema + separator + '%s floor, section %s' % ( '4-th', 'C'),
              u'Bema, section B'                    : bema + separator + '%s floor, section %s' % ( '4-th', 'B'),
              u'WPB Strzegomska 52B.112'            : wpb % ('52B','112'),
              u'WPB, 52B.112'                       : wpb % ('52B', '112'),
              u'WPB, 52B.203'                       : wpb % ('52B', '203'),
              u'WPB, 56A, room 003'                 : wpb % ('56A', '003'),
              u'WPB, Strzegomska 52B'               : wpb % ('52B', '203'),
              u'WPB, Strzegomska 52B.112'           : wpb % ('52B', '112'),
              u'WPB, Strzegomska 52B.203'           : wpb % ('52B', '203'),
              }
    assert name in mapper
    return mapper[name]


def migrate_users():
    # adding users to new db
    users = cursor.execute('SELECT * FROM users').fetchall()
    # normalized_users = [u[1:4] for u in users]
    admins = Group.objects.get(name='Librarians') #TODO: spytac czy to o to chodzi
    readers = Group.objects.get(name='Readers')
    for u in users:
        new_user = User.objects.create_user(username=u[3], email=u[3], password=u[2]+'74')
        new_user.first_name = u[1]
        new_user.last_name = u[2]
        if u[5] == 1:
            new_user.groups.add(admins)
        new_user.groups.add(readers)
        new_user.is_active = False
        if u[1][-1] == 'a':
            new_user.shoe_size = 37
        else:
            new_user.show_size = 46
        if not u[6]:
            new_user.is_active = True
        new_user.save()
        if u[6]:
            p = new_user.userprofile
            p.awaits_activation = False
            p.save()
    maru = User.objects.create_user(username='maru', email='brzoza@jabster.pl', password='lala')
    maru.is_superuser = True
    maru.is_staff = True
    maru.save()

def migrate_locations():
    # adding locations to new db
    books_desc_list = list(set([e[6] for e in old_books]))
    books_desc_tuples= map(description_to_tuple, books_desc_list)
    normalized_locations = map(normalize_location, [e[0] for e in books_desc_tuples])
    building_to_location_object = {}
    for building, details in [l.split(';') for l in normalized_locations]:
        b, _ = Building.objects.get_or_create(name=building)
        location, _ = Location.objects.get_or_create(building=b, details=details)
        building_to_location_object[building+';'+details] = location

    
    def u(name):
        name = name.lower()
        return User.objects.get(username=name+'@nsn.com')

    mapper = {
        u'Rafal Gorski'                 : u('rafal.gorski'),
        u'Sylwia Pilarska'              : u('sylwia.pilarska'),
        u'elzbieta.jozefowska@nsn.com'  : u('elzbieta.jozefowska'),
        u'Elzbieta Jozefowska'          : u('Elzbieta.Jozefowska'), 
        u'Agnieszka Sniezewska'         : u('Agnieszka.Sniezewska'), 
        u'Samanta Lempart'              : u('Samanta.Lempart'), 
        u'elzbieta.jozefowska@nsn.com'  : u('elzbieta.jozefowska'),
        u'Elzbieta Jozefowska'          : u('Elzbieta.Jozefowska'), 
        u'Karolina Zakrocka'            : u('Karolina.Zakrocka'), 
        u'Monika Cwynar-K\u0119pa'      : u('Monika.Cwynar-Kepa'), 
        u'Sylwia Pilarska'              : u('Sylwia.Pilarska'), 
        u'Sylwia Pilarska'              : u('Sylwia.Pilarska'), 
        u'Rafal Gorski'                 : u('Rafal.Gorski'), 
        u'Agnieszka Sniezewska'         : u('Agnieszka.Sniezewska'), 
        u'Rafal Gorski'                 : u('Rafal.Gorski'), 
        u'Agnieszka Sniezewska'         : u('Agnieszka.Sniezewska'), 
        u'Edyta Gorecka'                : u('Edyta.Gorecka'), 
        u'Agnieszka Sniezewska'         : u('Agnieszka.Sniezewska'), 
        u'elzbieta.jozefowska@nsn.com'  : u('elzbieta.jozefowska'),
        u'Elzbieta Jozefowska'          : u('Elzbieta.Jozefowska'), 
        u'elzbieta.jozefowska@nsn.com'  : u('elzbieta.jozefowska'),
        u'Elzbieta Jozefowska'          : u('Elzbieta.Jozefowska'), 
        u'Rafal Gorski'                 : u('Rafal.Gorski'), 
        u'Edyta G\xf3recka'             : u('Edyta.Gorecka'), 
        u'Rafal Gorski'                 : u('Rafal.Gorski'), 
        u'Edyta G\xf3recka'             : u('Edyta.Gorecka'), 
        u'Rafa\u0142 g\xf3rski'         : u('Rafal.gorski'), 
        u'Rafal Gorski'                 : u('Rafal.Gorski'), 
        u'Elzbieta Jozefowska'          : u('Elzbieta.Jozefowska'), 
        u'Rafal G\xf3rski'              : u('Rafal.Gorski'), 
        u'Karolina Zakrocka'            : u('Karolina.Zakrocka'), 
        u'Samanta Lempart'              : u('Samanta.Lempart'), 
        u'Rafal G\xf3rski'              : u('Rafal.Gorski'), 
        u'Karolina Zakrocka'            : u('Karolina.Zakrocka'), 
        u'Edyta Gorecka'                : u('Edyta.Gorecka'), 
        u'Elzbieta Jozefowska'          : u('Elzbieta.Jozefowska'), 
        u'Elzbieta Jozefowska'          : u('Elzbieta.Jozefowska'), 
        u'Rafa\u0142 G\xf3rski'         : u('Rafal.Gorski'), 
        u'Agnieszka Sniezewska'         : u('Agnieszka.Sniezewska'), 
        u'Samanta Lempart'              : u('Samanta.Lempart'), 
    }


    def normalize_name(name):
        assert name in mapper
        return mapper[name]


    normalized_maintainers = map(normalize_name, [e[2] for e in books_desc_tuples])
    for building, cc, maintainer in books_desc_tuples:
        # add maintainer to location
        maintainer = normalize_name(maintainer)
        location = building_to_location_object[normalize_location(building)]
        location.maintainer.add(maintainer)
        location.save()

        # add cost center
        CostCenter.objects.get_or_create(name=cc)[0].save()


def remove_hash(arg_title):
    title = arg_title
    if not "#" in title:
        return title
    else:
        hash_deleter = re.compile(r"(.*)#\d(.*)")
        title = ''.join( hash_deleter.match(title).groups() )
        assert title
        return title
    
author_mapper_dict = {
    u'Herb, Sutter'   : u'Herb Sutter',
    u'Jacob, West'    : u'Jacob West',
    u'Silberschatz'   : u'Abraham Sielberschatz',
    u'Galvin'         : u'Peter Baer Galvin', 
    u'Gagne'          : u'Greg Gagne',
    u'Ken Shwaber'    : u'Ken Schwaber',
    u'Kent Back'      : u'Kent Beck',
    u'P.Walke'        : u'P. Walke',
    u'P. Seidenberg'  : u'P. Seidenberg',
    u'Etsher Derby'   : u'Esther Derby',
    u'M.P.Althoff'    : u'M. P. Althoff',
    u'Ralph Johanson' : u'Ralph Johnson',
    u'richard Helm'   : u'Richard Helm',
    u'T.RudeBusch'    : u'T.Rudebusch',
    u'T.Rudebusch'    : u'T. Rudebusch',
    u'Hays W. "Skip" McCormick III' : "Hays W. 'Skip' McCormick III",
    }
def normalize_author(a):
    a = a.strip()
    if a in author_mapper_dict:
        return author_mapper_dict[a]
    else:
        return a


ID = 'identity, not tile should ever be this:)'                                                                                                                              
title_mapper_dict = {
     u'1913A Exchanging and Transforming Data Using XML and XSLT'                                  : ID,
     u'3G Evolution: HSPA and LTE for Mobile Broadband '                                           : ID,
     u'7 nawyk\xf3w skutecznego dzia\u0142ania'                                                    : ID,
     u'ANT in Action'                                                                              : ID,
     u'ATM Networks, concepts, protocols, applications'                                            : ID,
     u'Accelerated C++. Practical Programming by Example '                                         : ID,
     u'Administering Microsort Office Project Server 2003'                                         : ID,
     u'Advanced COBRA Programming with C++'                                                        : ID,
     u'Advanced FPGA Design'                                                                       : ID,
     u'Advanced Programming in the UNIX Enviroment. Second edition'                                : ID,
     u'Advanced UNIX Programming, second edition'                                                  : ID,
     u'Advanced Windows Debugging'                                                                 : ID,
     u"Agile & Iterative Development. A Manager's Guide"                                           : ID,
     u'Agile Adoption Patterns, a roadmap to Organizational Success'                               : ID,
     u'Agile Coaching '                                                                            : ID,
     u'Agile Estimating and Planning'                                                              : ID,
     u'Agile Estimating and Planning, Robert C. Martin Series'                                     : ID,
     u'Agile Project Management with Scrum '                                                       : ID,
     u'Agile Retrospectives. Making Good Teams Great'                                              : ID,
     u'Agile Retrospectives. Making Good Teams Great '                                             : ID,
     u'Agile Software Development with Scrum'                                                      : ID,
     u'Agile Software Development: Principles, Patterns and Practices'                             : ID,
     u'An Embedded Software Primer '                                                               : ID,
     u'An Introduction to TTCN-3 '                                                                 : ID,
     u'Ant. The Definitive Giude'                                                                  : ID,
     u'AntiPatterns. Refactoring Software, Architectures, and Projects in Crisis'                  : ID,
     u'Antipatterns: Identification Refactoring, and Management '                                  : u'Antipatterns: Identification, Refactoring and Management',
     u'Antipatterns: Identification, Refactoring, and Management '                                 : u'Antipatterns: Identification, Refactoring and Management',
     u'Applied C++ : Practical Techniques for Building Better Software'                            : ID,
     u'Biblioteka Standardowa C++'                                                                 : ID,
     u'C++ 50 efektywnych sposob\xf3w na udoskonalenie Twoich program\xf3w'                        : ID,
     u'C++ Coding Standards'                                                                       : ID,
     u'C++ Gotchas: Avoiding Common Problems in Coding and Design'                                 : ID,
     u'C++ How to program 7-th edition'                                                            : ID,
     u'C++ Network Programming, vol. 1 '                                                           : ID,
     u'C++ Network Programming, vol. 2 '                                                           : ID,
     u'C++ Template Metaprogramming (Concepts, Tools, and Techniques from Boosts and Beyond)'      : ID,
     u'C++ szablony. Vademecum profesjonalisty'                                                    : ID,
     u'CDMA Principles of Spread Spectrum Communication'                                           : ID,
     u'Circuit Design with VHDL'                                                                   : ID,
     u'Clean Code. A Handbook of Agile Software Craftsmanship '                                    : ID,
     u'Code Complete, second edition'                                                              : ID,
     u'Communication Systems for the Mobile Information Society'                                   : ID,
     u'Communities of Practice'                                                                    : ID,
     u'Compilers. Principles, Techniques & Tools'                                                  : ID,
     u'Computer organization and Design. The Hardware/Software interface'                          : ID,
     u'Continuous Integration - Improving Software Quality '                                       : ID,
     u'Contributing to Eclipse'                                                                    : ID,
     u'Convergence Technologies for 3G Networks (IP, UMTS, EGPRS ATM)'                             : ID,
     u'DEV475 Mastering Object-Oriented Analysis and Design with UML, 2.0. Student Exercise Guide' : ID,
     u'DEV475 Mastering Object-Oriented Analysis and Design with UML, 2.0. Student Guide'          : ID,
     u'DEV475 Mastering Object-Oriented Analysis and Design with UMP 2.0. Student Appendix'        : ID,
     u'Data Center Fundamentals'                                                                   : ID,
     u'Design Patterns  ( Elements of Reusable Object-Orineted Software )'                         : u'Design Patterns ( Elements of Reusable Object-Orineted Software )',
     u'Design Patterns  (Elements of Reusable Object-Oriented Software)'                           : u'Design Patterns ( Elements of Reusable Object-Orineted Software )',
     u'Design Patterns Explained'                                                                  : ID,
     u'Designing Embededed Hardware'                                                               : ID,
     u'Designing Interfaces: Patterns for Effective Interaction Design'                            : ID,
     u'Digital Filters, third edition'                                                             : ID,
     u'Digital Signal Processing. A practical Guide for Engineers and Scientists'                  : ID,
     u'Eclipse Plug-ins'                                                                           : ID,
     u'Eclipse Rich Client Platform'                                                               : ID,
     u'Effective IT Project Management'                                                            : ID,
     u'Effective Java 2-nd edition'                                                                : ID,
     u'Effective STL (50 Specific Ways to Improve Your Use of the Standard Template Library)'      : ID,
     u'Embedded Linux Primer'                                                                      : ID,
     u'Embedded Systems Dictionary'                                                                : ID,
     u'Embeded Linux System Design and Development'                                                : ID,
     u'Essential C++'                                                                              : ID,
     u'Essential Linux Device Drivers'                                                             : ID,
     u'Evolved Packet System (EPS); The LTE an SAE evolution of 3G UMTS'                           : ID,
     u'Exceptional C++ Style '                                                                     : ID,
     u'Extreme Programming Explained. Embrace Change'                                              : ID,
     u'Finland, Cultural Lone Wolf'                                                                : ID,
     u'Finland, culture smart!'                                                                    : ID,
     u'Fit for developing software. Framework for Integrated Tests'                                : ID,
     u'Fundamentals of WiMAX (Understanding Broadband Wireless Networking)'                        : ID,
     u'Getting Organized Improving focus, organization and productivity'                           : ID,
     u'Guide to Advanced Software Testing'                                                         : ID,
     u'HSDPA/HSUPA for UMTS'                                                                       : ID,
     u'Hard Facts'                                                                                 : ID,
     u'Head First Design Patterns'                                                                 : ID,
     u'Head First EJB'                                                                             : ID,
     u'Head First: Object-Oriented, Analysis&Design'                                               : ID,
     u'High Availability and Disaster Cecover. Concepts, design, implementation'                   : ID,
     u'High performance TCP/IP networking. Concepts, issues, and solutions'                        : ID,
     u"IBM Rational ClearCase, Ant, and CruiseControl. The Java Developer's Guide to Accelerating and Automating the Build Process"   : ID,
     u'Imperfect C++'                                                                              : ID,
     u'Implementation Patterns'                                                                    : ID,
     u'Implementing Lean Software Development'                                                     : ID,
     u'Inside The C++ Object Model'                                                                : ID,
     u'In\u017cynieria oprogramowania. Testowanie system\xf3w obiektowych (modele, wzorce i narzdzia)'  : ID,
     u'Java Concurrency in Practice '                                                              : ID,
     u'Java Puzzlers'                                                                              : ID,
     u'Jednominutowy Mened\u017cer'                                                                : ID,
     u'Jednominutowy Mened\u017cer spotyka ma\u0142p\u0119'                                        : ID,
     u'J\u0119zyk C++ Standardy kodowania'                                                         : ID,
     u'Klasyka Informatyki. Algorytmy + struktury danych = programy'                               : ID,
     u'Klasyka informatyki. J\u0119zyk C++'                                                        : ID,
     u'LINUX Device Drivers'                                                                       : ID,
     u'LINUX Serwery Bezpiecze\u0144stwo'                                                          : ID,
     u'LTE for UMTS   (OFDMA and SC-FDMA Based Radio Access)'                                      : ID,
     u'Large-Scale C++ Software Design'                                                            : ID,
     u'Large-scale Software Architecture (A parctical guide using UML)'                            : ID,
     u'Leading Self-Directed Work Teams'                                                           : ID,
     u'Leading Teams, Setting the Stage for Great Performances'                                    : ID,
     u'Learning Python'                                                                            : ID,
     u'Linkers and Loaders'                                                                        : ID,
     u'Linux Kernel Development, second edition'                                                   : ID,
     u'MIMO wireless communications'                                                               : ID,
     u'MPC 8260 user manual'                                                                       : ID,
     u'Managing the Testing Process, 2-nd edition'                                                 : ID,
     u'Mastering Perl/Tk'                                                                          : ID,
     u'Memory Programming Concept in C and C++'                                                    : ID,
     u"Microsoft Windows Server 2003 Administrator's Companion"                                    : ID,
     u'Mobile Inter-Networking with IPv6'                                                          : ID,
     u'Mobile Radio Communications, second edition'                                                : ID,
     u'Modern C++ Design '                                                                         : ID,
     u'More Exceptional C++'                                                                       : ID,
     u'Motywacja pod lup\u0105'                                                                    : ID,
     u'Network Seciurity Architectures'                                                            : ID,
     u'Nowoczesne projektowanie w C++'                                                             : ID,
     u'Numerical Recipes. The Art of Scietific Computing'                                          : ID,
     u'Operating System Concepts, seventh edition'                                                 : ID,
     u'Oprogramowanie komponentowe, obiekty to za ma\u0142o'                                       : ID,
     u'Overcoming the Five dysunctions of a team a field guide'                                    : ID,
     u'Peopleware. Productive Projecta and Teams'                                                  : ID,
     u'Performance Solutions. A Practical Guide to Creating Responsive, Scalable Software'         : ID,
     u'Perl Receptury'                                                                             : ID,
     u'Practical Programming in Tcl and Tk'                                                        : ID,
     u'Practical Qt'                                                                               : ID,
     u'Practical Statecharts in C/C++ '                                                            : ID,
     u'Pragmatic Unit Testing in JAVA with JUnit'                                                  : ID,
     u'Programming Embedded Systems 2nd Edition'                                                   : ID,
     u'Programming Perl 3-rd edition'                                                              : ID,
     u'Programming with Qt, 2nd edition, Covers Qt3'                                               : ID,
     u'Real-Time Design Patterns. Robust Scalable Architecture for Real-Time Systems'              : ID,
     u'Real-Time Embedded System and Components'                                                   : ID,
     u'Refactoring To Patterns '                                                                   : ID,
     u'Refactoring, improving the Design of Existing Code '                                        : u'Refactoring: Improving the Design of Existing Code ',
     u'Refactoring: Improving the Design of Existing Code '                                        : u'Refactoring: Improving the Design of Existing Code ',
     u'Risk Management for IT Projects'                                                            : ID,
     u'Ruminations on C++'                                                                         : ID,
     u'SCJD Exam with J2SE 5'                                                                      : ID,
     u'SOLARIS 8, Sparc Platform Edition for Sun Computers Systems'                                : ID,
     u'SWT: The Standard Widget Toolkit; Volume: 1'                                                : ID,
     u'Scaling Lean & Agile Development '                                                          : ID,
     u'Scrum and XP from the Trenches. How we do Scrum'                                            : ID,
     u'Secure Programming with Static Analysis'                                                    : ID,
     u'Signaling System , fourth edition'                                                          : ID,
     u'Small Memory Software'                                                                      : ID,
     u'Sofrtawre Portability with imake'                                                           : ID,
     u'Software Engineering. Principles and Practice'                                              : ID,
     u'Software Estimation, Demistyfying the Black Art'                                            : ID,
     u'Software Testing, 2-nd edition'                                                             : ID,
     u'Solaris 10 System Administration Part 1 Exam Prep'                                          : ID,
     u'Solaris Internals Solaris 10 and opensolaris kernel architecture'                           : ID,
     u'Sprawne Zarz\u0105dzanie projektami metod\u0105 SCRUM'                                      : ID,
     u'Symfonia C++'                                                                               : ID,
     u'Szko\u0142a programowania, J\u0119zyk C++'                                                  : ID,
     u'TCP/IP Illustrated, vol. 1 (The Protocols)'                                                 : ID,
     u'TCP/IP Illustrated, vol. 2 (The Implementation)'                                            : ID,
     u'Tektronix K1297-G20, June, 2000'                                                            : ID,
     u'Test-Driven Development: By Example '                                                       : ID,
     u'Test-Driven Devlopment: A Practical guide'                                                  : ID,
     u'Test-Driven, Practical TDD and Acceptance TDD for Java Developers'                          : ID,
     u'The Annotated C++ reference Manual'                                                         : ID,
     u'The Art of Assembly Language'                                                               : ID,
     u'The Art of Computer Programming vol.1 (Fundamental Algorithms 3rd ed.)'                     : ID,
     u'The Art of Computer Programming vol.2 (Seminumerical Algorithms 3rd ed.)'                   : ID,
     u'The Art of Computer Programming vol.3 (Sorting and Searching 2nd ed.)'                      : ID,
     u'The Art of Debugging with GDB, DDD, and Eclipse'                                            : ID,
     u'The C++ Standard Library Extensions. A tutrial and Reference'                               : ID,
     u'The C++ Standard Library, A Tutorial and reference'                                         : ID,
     u'The DSP Handbook. Algorithms, Applications and Design Tehniques'                            : ID,
     u'The Design and Evolution of C++'                                                            : ID,
     u'The Enterprise and Scrum '                                                                  : ID,
     u'The Five Dysfunctions of a Team'                                                            : ID,
     u'The Future of Management'                                                                   : ID,
     u'The Pragmatic Programmer'                                                                   : ID,
     u"The Software Test Engineer's Handbook"                                                     : ID,
     u'The Theory and practice of FPGA-BASED computing'                                            : ID,
     u'The Time Trap, classic book on TIme management 4th edition.'                                : ID,
     u'The Toyota Way'                                                                             : ID,
     u'The UMTS Network and Radio Access Technology'                                               : ID,
     u'The best software writing I'                                                                : ID,
     u'Thinking in C++, tom 2'                                                                     : ID,
     u'Toward Zero-Defect Programming'                                                             : ID,
     u'Types and Programming Languages'                                                            : ID,
     u'UML Distilled. Third Edition. A brief Guide to the Standard Object Modeling Language'       : ID,
     u'UMTS Mobile Communications for the Future'                                                  : ID,
     u'UMTS Signaling, second edition '                                                            : ID,
     u'UMTS Systemy telefonii kom\xf3rkowej trzeciej generacji'                                    : ID,
     u'UMTS The Fundamentals'                                                                      : ID,
     u'UNIX  programowanie us\u0142ug sieciowych, tom 2 (komunikacja mi\u0119dzyprocesowa)'        : ID,
     u'UNIX Power Tools'                                                                           : ID,
     u'UNIX in a nutshell'                                                                         : ID,
     u'UNIX programowanie us\u0142ug sieciowych, tom 1, (API: gniazda i XTI)'                      : ID,
     u'Understanding Digital Signal Processing'                                                    : ID,
     u'Understanding the linux kernel'                                                             : ID,
     u'Unit Test Frameworks'                                                                       : ID,
     u'User Stories Applied for Agile Software Development '                                       : ID,
     u'VHDL Programming by Example, fourth edition'                                                : ID,
     u'Vademecum Teleinformatyka III'                                                              : ID,
     u'WIMAX Technology for Broaband Wireless Access'                                              : ID,
     u'Why programs fall. A guide to systematic debugging'                                         : ID,
     u'Working effectively with legacy code '                                                      : ID,
     u'Write Great Code vol.1   (Understanding the Machine)'                                       : u'Write Great Code vol.1   (Understanding the Machine)',
     u'Write Great Code vol.1  (Understanding the Machine)'                                        : u'Write Great Code vol.1   (Understanding the Machine)',
     u'Write Great Code vol.2  (Tthinking low level writing high-level)'                           : u'Write Great Code vol.2  (Tthinking low level writing high-level)',
     u'Write Great Code vol.2  (Tthinking low level writing high-level)1'                          : u'Write Great Code vol.2  (Tthinking low level writing high-level)',
     u'Write Portable Code (an Introduction to Developing software for Multile Platforms)'         : ID,
     u'Writing Effective Use Cases '                                                               : ID,
     u'fundamentals of Spectrum Analysis'                                                          : ID,
     u'programowanie zastosowa\u0144 sieciowych w systemie UNIX'                                   : ID,
     u'xUnit Test Patterns - Refactoring, Test Code '                                              : ID,
}

for k in title_mapper_dict:
    if title_mapper_dict[k] == ID:
        title_mapper_dict[k] = k

def normalize_title(title):
    title = remove_hash(title)
    assert title in title_mapper_dict, Exception(title)
    return title_mapper_dict[title].strip()

    # this is not executed, its archival
    if title in title_mapper_dict:
        return title_mapper_dict[title]
    else:
        return None


# modify a few books not to contain e.g. authors separated by apostrophe
books = list(old_books)
i = books.index( (68, None, u'ANT in Action', u"Steve Loughran' Erik Hatcher", u'English', None, u'location: Bema Plaza, 3-rd floor, section B\r\nCC: 4021018\r\ncontact: Sylwia Pilarska', 0, u'see description', 1274738400000L, None, None, 0, None) )
books[i] = (68, None, u'ANT in Action', u"Steve Loughran, Erik Hatcher", u'English', None, u'location: Bema Plaza, 3-rd floor, section B\r\nCC: 4021018\r\ncontact: Sylwia Pilarska', 0, u'see description', 1274738400000L, None, None, 0, None) 
i = books.index( (39, 18, u'3G Evolution: HSPA and LTE for Mobile Broadband #1', u'Erik Dahlman, Stefan Parkvall, Johan Skold and Per Beming', u'English', None, u'Location: WPB, 56A, room 003\r\nCC: 4021024\r\nContact: Monika Cwynar-K\u0119pa', 2, u'Krzysztof Kosmider', 1273615200000L, 1277503200000L, None, 0, u'Krzysztof Kosmider') )
books[i] = (39, 18, u'3G Evolution: HSPA and LTE for Mobile Broadband #1', u'Erik Dahlman, Stefan Parkvall, Johan Skold, Per Beming', u'English', None, u'Location: WPB, 56A, room 003\r\nCC: 4021024\r\nContact: Monika Cwynar-K\u0119pa', 2, u'Krzysztof Kosmider', 1273615200000L, 1277503200000L, None, 0, u'Krzysztof Kosmider')
i = books.index((153, None, u'Exceptional C++ Style #2', u'Herb, Sutter', u'English', None, u'Location: Bema Plaza, 4th floor, section B\r\nCC: 4021121\r\nContact: Agnieszka Sniezewska', 0, u'see description', 1275256800000L, None, None, 0, None))
books[i] = (153, None, u'Exceptional C++ Style #2', u'Herb Sutter', u'English', None, u'Location: Bema Plaza, 4th floor, section B\r\nCC: 4021121\r\nContact: Agnieszka Sniezewska', 0, u'see description', 1275256800000L, None, None, 0, None)
i = books.index((215, None, u'Secure Programming with Static Analysis', u'Brian Chess, Jacob, West', u'English', None, u'Location: WPB, Strzegomska 52B.203\r\nCC: 4021136\r\nContact: Samanta Lempart', 0, u'see description', 1276120800000L, None, None, 0, None))
books[i] = (215, None, u'Secure Programming with Static Analysis', u'Brian Chess, Jacob West', u'English', None, u'Location: WPB, Strzegomska 52B.203\r\nCC: 4021136\r\nContact: Samanta Lempart', 0, u'see description', 1276120800000L, None, None, 0, None)
    

def migrate_authors():
    # extract authors from books
    authors = [a[3] for a in books]

    # transform authors to a list of authors
    authors = [  ( a.split(',') )  for a in authors  ]
    authors = reduce (lambda x,y: x + y, authors)
    authors = map(unicode.strip, authors)
    authors = map(normalize_author, authors)
    #authors = list(set(authors))
    #authors.sort()

    for a in authors:
        Author.objects.get_or_create(name=a)

    return authors
    
def migrate_books():
    for book in books:
        authors = book[3].split(',')
        authors = map(normalize_author, authors)
        authors = [Author.objects.get(name=a) for a in authors ]
        b, created = Book.objects.get_or_create(title=normalize_title(book[2]))
        if created:
            b.author = authors
            b.save()


def migrate_copies():
    contact_user_mapper_dict = {
        u'Agnieszka Sniezewska'            : User.objects.get(username='agnieszka.sniezewska@nsn.com'),
        u'Edyta Gorecka'                   : User.objects.get(username='edyta.gorecka@nsn.com'),
        u'Edyta G\xf3recka'                : User.objects.get(username='edyta.gorecka@nsn.com'),
        u'Elzbieta Jozefowska'             : User.objects.get(username='elzbieta.jozefowska@nsn.com'),
        u'elzbieta.jozefowska@nsn.com'     : User.objects.get(username='elzbieta.jozefowska@nsn.com'),
        u'Karolina Zakrocka'               : User.objects.get(username='karolina.zakrocka@nsn.com'),
        u'Monika Cwynar-K\u0119pa'         : User.objects.get(username='monika.cwynar-kepa@nsn.com'),
        u'Rafal Gorski'                    : User.objects.get(username='rafal.gorski@nsn.com'),
        u'Rafal G\xf3rski'                 : User.objects.get(username='rafal.gorski@nsn.com'),
        u'Rafa\u0142 G\xf3rski'            : User.objects.get(username='rafal.gorski@nsn.com'),
        u'Rafa\u0142 g\xf3rski'            : User.objects.get(username='rafal.gorski@nsn.com'),
        u'Samanta Lempart'                 : User.objects.get(username='samanta.lempart@nsn.com'),
        u'Sylwia Pilarska'                 : User.objects.get(username='sylwia.pilarska@nsn.com'),
        }
    import random
    for book in books:
        title = normalize_title(book[2])
        try:
            b = Book.objects.get(title=title)
        except:
            raise Exception("couldn't find {1} ".format(title))
        desc = book[6]
        location_name, cc, contact = description_to_tuple(desc)
        location_name = normalize_location(location_name)
        building, details = location_name.split(';')
        try:
            building = Building.objects.get(name=building)
        except:
            raise Exception("couldn't find {1} ".format(building))
        try:
            location = Location.objects.get(building=building, details=details)
        except:
            raise Exception("couldn't find {1} ".format(building))
        try:
            cc, created = CostCenter.objects.get_or_create(name=cc.strip())
        except:
            raise Exception("couldn't find cost center{1} ".format(cc))
        maintainer = contact_user_mapper_dict[contact]
        maintainer = User.objects.get(username=maintainer)
        
        state_ok = State.objects.get(name='OK')
        state_lost = State.objects.get(name='Lost')

        copy = BookCopy(shelf_mark=str(book[0]), 
                        book=b,
                        cost_center=cc,
                        location=location,
                        state=state_ok if not book[12] else state_lost
                        )
        copy.save()

        if maintainer not in location.maintainer.all():
            location.maintainer.add(maintainer)

def migrate_events():
    events = list(cursor.execute("""SELECT e.id_book, u.login, e.book_date, b.due_date, e.borrow_date, e.due_date 
                                      FROM events e 
                                      JOIN users u USING (id_user) 
                                      JOIN books b ON e.id_book = b.id_book"""
                                  ).fetchall())
    es = map(lambda rec: rec[0:2] + tuple(map(lambda d: datetime.fromtimestamp(d/1000.0) if d else None,
                                              rec[2:]
                                             )
                                         ),
             events)
    archival, _created = User.objects.get_or_create(username="archival", email="none@none.pl")
    archival.is_active = False
    archival.save()
    profile = archival.userprofile
    profile.awaits_activation = False
    profile.save()

    for (shelf_mark, email, reservation_start, reservation_end, rental_start, rental_end) in es:
        user = User.objects.get(email=email)
        if not reservation_end:
            reservation_end = reservation_start + timedelta(30)
        reservation = Reservation(
            book_copy = BookCopy.objects.get(shelf_mark=str(shelf_mark)),
            for_whom = User.objects.get(email=email),
            start_date = reservation_start,
            end_date = reservation_end,
            who_reserved = user,
            when_reserved = reservation_start,
            who_cancelled = None,
            when_cancelled = None,
            active_since = reservation_start,
            shipment_requested = False
            )
        reservation.save()

        if rental_start:
            rental = Rental(
                reservation = reservation,
                start_date = rental_start,
                end_date = rental_end if rental_end else None,
                who_handed_out = archival,
                who_received = archival if rental_end else None
                ).save()





if __name__ == "__main__":
    if raw_input(['migrate?']) == 'yes':
        main(True)

def main(erase=False):
    from dbfiller import clear_db, add_states, add_phone_types, populate_groups, main
    '''
    clear_db()
    add_states()
    add_phone_types()
    populate_groups()
    '''
    main()

    if erase:
        pprint('erasing users')
        User.objects.filter(id__gt=0).delete()

        pprint('erasing user profiles')
        UserProfile.objects.filter(user__id__gt=0).delete()

        pprint('erasing buldings')
        Building.objects.all().delete()

        pprint('erasing locations')
        Location.objects.all().delete()

        pprint('erasing copies')
        BookCopy.objects.all().delete()

        pprint('erasing authors')
        Author.objects.all().delete()

        pprint('erasing books')
        Book.objects.all().delete()
    
    pprint ('erasing copies')
    BookCopy.objects.all().delete()

    pprint('migrating users')
    migrate_users()

    pprint('migrating locations')
    migrate_locations()

    pprint('migrating authors')
    migrate_authors()

    pprint('migrating books')
    migrate_books()

    pprint('migrating copies')
    migrate_copies()

    if erase:
        pprint('restoring four users')
        add_users()
