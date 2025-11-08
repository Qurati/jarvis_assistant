#=================================
# хелпер для комманд используемых
# в jarvise
#=================================
class helper_commands:

    def write_all_commands():
        __all_commands = ['джарвис', 'привет', 'доброе утро', 
                        'спасибо', 'создай новый элемент',
                       'напиши все комманды', 'неправильно']
        count_command = 0

        print('-----------КОМАНДЫ-----------')
        for x in __all_commands:
            count_command += 1
            print(f'команда {count_command} > {x}')

