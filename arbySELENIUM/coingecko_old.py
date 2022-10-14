#!/usr/local/bin/python3

import ccxt, pyotp
from driver_information import *

#_URLS

class exchange():
	def __init__(self,driver,logged_in=False):

		self.login_site = 'https://www.coingecko.com/en'

		#self.google_sender = "coinex"

		#google = ''

		self.omit_list = ['pro','the']

		self.exchange = ccxt.coinmarketcap()

		self.driver = driver

		self.wait = WebDriverWait(self.driver, 20)

		#self.totp = pyotp.TOTP(google)

		self.cache_totp = None
		self.verification_pause = None

		self.logged_in = logged_in

		self.stop_thread = 'OFF'

		threading.Thread(target=self.verification_check).start()

		
	def verification_check(self):

		while True:

			t0 = time.time()
			while (time.time()-t0) < 15:
				time.sleep(1)
				if self.stop_thread == 'ON':
					self.stop_thread = 'DONE'
					return None

			#print(f'CHECKING! {self.exchange.id}')
			if self.verification_pause == True:
				chump.send_message(f"CHECK SLIDER! Exchange: {self.exchange.id.upper()} !")
				
	def login_check(self):
		wait = WebDriverWait(self.driver,5)
		time.sleep(5)
		soup = reload(self.driver)
		return wait.until(EC.element_to_be_clickable((By.XPATH,get_xpath(soup.find('input',{'type':'password'})))))

	def login(self):
		self.driver.get(self.login_site)

	def does_it_exist(self,exchange_1,_exchange_2):
		pass

	def screen(self,currency,exchange_1,exchange_2):
		
		#if self.driver.current_url != "https://www.coingecko.com/en/"
		self.driver.get("https://www.coingecko.com/en/")

		exchange_1 = eval(f"ccxt.{exchange_1}()")
		exchange_2 = eval(f"ccxt.{exchange_2}()")
		
		soup = reload(self.driver)
		top_page = self.driver.find_element_by_xpath('/html')
		#self.driver.execute_script("window.scrollTo(0, 0);")
		#soup = reload(self.driver)
		input_bar = self.driver.find_element_by_xpath(get_xpath(soup.find('input',{'placeholder':'Search'})))
		self.driver.execute_script("arguments[0].scrollIntoView();", input_bar)

		self.driver.find_element_by_xpath('/html').click()
		for i in range(50):
			input_bar.send_keys(Keys.BACKSPACE)
		input_bar.click()

		#time.sleep(1)
		input_bar.send_keys(currency)
		time.sleep(1)
		soup = reload(self.driver)

		while True:
			try:
				dropdown = soup.find('ul',{'class':'list-reset relevant-results'}).find_all('li',{'class': re.compile('text-sm mt-1')})
				break
			except AttributeError:
				time.sleep(0.1)
				print('Retrying...')
				soup = reload(self.driver)
				self.driver.find_element_by_xpath('/html').click()
				self.driver.find_element_by_xpath(get_xpath(soup.find('input',{'placeholder':'Search'}))).click()
		try:
			entries = [slot for slot in dropdown if f"({currency})" in slot.find('span',{'style':'width:70vw;'}).text]
		except AttributeError:
			raise TimeoutError('COINGECKO FIX.')


		if len(entries) > 1:
			return {'status': 'DUPLICATE SYMBOLS'}

		if len(entries) == 0:
			return {'status': 'NO CURRENCY FOUND'}

		for entry in entries:
			
		link = entries[0].a.get('href')

		self.driver.get(link)

		name = self.driver.current_url.split('https://www.coingecko.com/en/coins/')[1]

		self.driver.get(self.driver.current_url+"#markets")

		checkmark = []

		while True:
			time.sleep(5)
			soup = reload(self.driver)
			
			table = soup.find_all('tbody',{'data-target':'gecko-table.paginatedShowMoreTbody'})[-1]

			old_slots = len(table.find_all('tr'))

			exchange_1_list = [x for x in exchange_1.name.lower().split(' ') if x not in self.omit_list]
			exchange_2_list = [x for x in exchange_2.name.lower().split(' ') if x not in self.omit_list]
			
			if 1 not in checkmark and (exchange_1.id.lower() in table.text.lower() or any(x in table.text.lower() for x in exchange_1_list)):
				checkmark.append(1)

			if 2 not in checkmark and (exchange_2.id.lower() in table.text.lower() or any(x in table.text.lower() for x in exchange_2_list)):
				checkmark.append(2)

			if len(checkmark) > 2:
				raise TimeoutError('WTF')

			if 1 in checkmark and 2 in checkmark:
				return {'status': 'FOUND', 'name': name, 'exchange': 'BOTH'}

			try:
				#button_element = self.driver.find_element_by_xpath(get_xpath(findbytext(soup,'a','Show More')[-1]))
				button_element = self.driver.find_element_by_xpath("/html/body/div[2]/div[4]/div[6]/div/div[2]/div/div[2]/div/div[2]/div/div[1]/div[3]/a")
				
			except IndexError:
				if len(checkmark) == 0:
					return {'status': 'NO EXCHANGE FOUND', 'name': name}

				elif len(checkmark) == 1:
					if checkmark[0] == 1:
						return {'status': 'FOUND', 'name': name, 'exchange': exchange_1.id}

					elif checkmark[0] == 2:
						return {'status': 'FOUND', 'name': name, 'exchange': exchange_2.id}

					else:
						raise TimeoutError(f'WTF 4')

				else:
					raise TimeoutError('WTF2')

			self.driver.execute_script("arguments[0].scrollIntoView();", button_element)
			self.driver.execute_script("window.scrollBy(0, -200);")
			print('Clicking again!')
			try:
				button_element.click()
			except Exception as e:
				if 'element not interactable' in str(e):
					if len(checkmark) == 0:
						return {'status': 'NO EXCHANGE FOUND', 'name': name}

					elif len(checkmark) == 1:
						if checkmark[0] == 1:
							return {'status': 'FOUND', 'name': name, 'exchange': exchange_1.id}

						elif checkmark[0] == 2:
							return {'status': 'FOUND', 'name': name, 'exchange': exchange_2.id}

						else:
							raise TimeoutError(f'WTF3')


				else:
					raise TimeoutError(f'WTF5 -> {str(e)}')

			while True:
				soup = reload(self.driver)
				table = soup.find_all('tbody',{'data-target':'gecko-table.paginatedShowMoreTbody'})[-1]
				new_slots = len(table.find_all('tr'))
				print(f'\nnew {new_slots}')
				print(f'old {old_slots}')
				if new_slots == old_slots:
					time.sleep(1)
				else:
					old_slots = new_slots
					break

		#input_bar.send_keys(Keys.ENTER)

if __name__ == '__main__':
	
	original = open_chrome()
	s = exchange(original)
	s.login()
	#s.withdraw('XRP',80,'rHcFoo6a9qT5NHiVn1THQRhsEGcxtYCV4d','296094211')
	
	#print(s.balance('BTC'))