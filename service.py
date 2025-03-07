from datetime import datetime
from dateutil.relativedelta import relativedelta
from prettytable import PrettyTable
import matplotlib.pyplot as plt
import numpy as np

def validation_date():
    status = False
    while not status:
        date = input('Введите дату начала кредита: ')
        try:
            date = datetime.strptime(date, '%d-%m-%Y')
            status = True
        except:
            print('Дата должна быть введена в формате дд-мм-гггг!\n')
    return date

def validation_float(str):
    status = False
    while not status:
        annual_rate = input(str)
        try:
            annual_rate = float(annual_rate)
            status = True
        except:
            print('Должно быть введено число!\n')
    return annual_rate

def validation_int(str):
    status = False
    while not status:
        annual_rate = input(str)
        try:
            annual_rate = int(annual_rate)
            status = True
        except:
            print('Должно быть введено целое число!\n')
    return annual_rate

def payment_data():
    user_choice = None
    while user_choice != '1' and user_choice != '2':
        user_choice = input('Вид платежа: ')
        if user_choice != '1' and user_choice != '2':
            print('Необходимо ввести 1 или 2!')
    return user_choice

USER_CHOICE = {
    '1': 'аннуитетный',
    '2': 'дифференцированный'
}

def print_table_or_chart(user_choice, annual_rate, property_value, initial_payment, mortgage_term, date, str):
    if user_choice == '1':
        table, graph, total_sum, overpayment = annuity_payment(annual_rate, property_value, initial_payment, mortgage_term, date, user_choice)
    elif user_choice == '2':
        table, graph, total_sum, overpayment = differentiated_payment(annual_rate, property_value, initial_payment, mortgage_term, date, user_choice)
    if str == 'table':
        print_table(total_sum, overpayment, table)
    elif str == 'chart':
        print_chart(mortgage_term, graph)
        print_pie(property_value, overpayment)

def print_table(total_sum, overpayment, table):
    print('Размер итоговой суммы с учетом первоначального взноса равен ' + f'{total_sum:,.2f}'.replace(',', ' '))
    print('Размер переплаты по кредиту равен ' + f'{overpayment:,.2f}'.replace(',', ' '))
    print(table)

def print_chart(mortgage_term, graph):
    months = np.linspace(1, mortgage_term * 12 + 1, mortgage_term * 12)
    fig, ax = plt.subplots()
    ax.stackplot(months, graph.values(), labels=graph.keys(), alpha = 0.8)
    ax.set_ylim(0, (graph['Основной долг'][0] + graph['Проценты'][0]) * 1.5)
    ax.set_xlim(1, mortgage_term * 12)
    ax.legend(reverse = True)
    ax.set_title('Структура платежей')
    ax.set_ylabel('Сумма, руб.')
    ax.set_xlabel('Платеж')
    plt.show()

def print_pie(property_value, overpayment):
    fig, ax = plt.subplots(figsize=(6, 4), subplot_kw=dict(aspect="equal"))
    data = [property_value, overpayment]
    legend_payment = [f'Основной долг\n{property_value:,.2f}'.replace(',', ' '), f'Проценты\n{overpayment:,.2f}'.replace(',', ' ')]
    wedges, texts = ax.pie(data, startangle=-40)
    bbox_props = dict(boxstyle="square,pad=0.3", fc="w", ec="k", lw=0.72)
    kw = dict(arrowprops=dict(arrowstyle="-"), bbox=bbox_props, zorder=0, va="center")
    for i, p in enumerate(wedges):
        ang = (p.theta2 - p.theta1)/2. + p.theta1
        y = np.sin(np.deg2rad(ang))
        x = np.cos(np.deg2rad(ang))
        horizontalalignment = {-1: "right", 1: "left"}[int(np.sign(x))]
        connectionstyle = f"angle,angleA=0,angleB={ang}"
        kw["arrowprops"].update({"connectionstyle": connectionstyle})
        ax.annotate(legend_payment[i], xy=(x, y), xytext=(1.35*np.sign(x), 1.4*y), horizontalalignment=horizontalalignment, **kw)
    ax.set_title('Соотношение основного долга и процентов по кредиту')
    plt.show()

def annuity_payment(annual_rate, property_value, initial_payment, mortgage_term, date, user_choice):
    credit_sum = property_value -  initial_payment
    monthly_rate = annual_rate / 12 / 100
    total_rate = (1 + monthly_rate) ** (mortgage_term * 12)
    monthly_payment = credit_sum * monthly_rate * total_rate / (total_rate - 1)
    total_sum = monthly_payment * mortgage_term * 12 + initial_payment
    overpayment = monthly_payment * mortgage_term * 12 - credit_sum
    percentage_part = credit_sum * monthly_rate
    main_part = monthly_payment - percentage_part
    table, graph = construct_table_and_graph(mortgage_term, user_choice, date, monthly_payment, main_part, percentage_part, credit_sum, monthly_rate)
    return table, graph, total_sum, overpayment

def differentiated_payment(annual_rate, property_value, initial_payment, mortgage_term, date, user_choice):
    credit_sum = property_value - initial_payment
    monthly_rate = annual_rate / 12 / 100
    main_part = credit_sum / (mortgage_term * 12)
    number_of_payments = credit_sum / main_part
    overpayment = monthly_rate * (number_of_payments + 1) / 2 * credit_sum
    total_sum = property_value + overpayment
    percentage_part = credit_sum * monthly_rate
    monthly_payment = main_part + percentage_part
    table, graph = construct_table_and_graph(mortgage_term, user_choice, date, monthly_payment, main_part, percentage_part, credit_sum, monthly_rate)
    return table, graph, total_sum, overpayment

def construct_table_and_graph(mortgage_term, user_choice, date, monthly_payment, main_part, percentage_part, credit_sum, monthly_rate):
    arr_main_part = []
    arr_percentage_part = []
    count = 1
    table = PrettyTable()
    table.field_names = ['Номер платежа', 'Дата', 'Размер платежа', 'Долг', 'Проценты', 'Остаток долга']
    while count <= mortgage_term * 12:
        arr_main_part.append(main_part)
        arr_percentage_part.append(percentage_part)
        credit_sum = credit_sum - main_part
        if count == mortgage_term * 12:
            credit_sum = 0
        table.add_row([
                        count, date.strftime("%d-%m-%Y"),
                        f'{monthly_payment:,.2f}'.replace(',', ' '),
                        f'{main_part:,.2f}'.replace(',', ' '),
                        f'{percentage_part:,.2f}'.replace(',', ' '),
                        f'{credit_sum:,.2f}'.replace(',', ' ')
                        ])
        count += 1
        date = date + relativedelta(months = 1)
        percentage_part = credit_sum * monthly_rate
        if user_choice == '1':
            main_part = monthly_payment - percentage_part
        elif user_choice == '2':
            monthly_payment = main_part + percentage_part
    graph = {'Основной долг': arr_main_part, 'Проценты': arr_percentage_part}
    return table, graph