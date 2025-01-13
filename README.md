# Sycash

Sycash is a Discord bot-based payment system that allows users to manage virtual currency, process payments, and handle transactions through multiple payment methods including PayPal, bank transfers, and cryptocurrency.



## Features

- **Multi-Payment Support**: Process payments via:
  - PayPal
  - Bank transfers
  - Cryptocurrency (via Coinbase Commerce)
  - Stripe integration

- **User Management**:
  - Account creation and verification
  - Email verification system
  - Session management
  - Balance tracking
  - User settings management

- **Security Features**:
  - Email verification with OTP
  - Encrypted data handling
  - Session timeout management
  - Secure payment processing

- **Discord Integration**:
  - Balance checking
  - Fund transfers between users
  - Withdrawal requests
  - Account management commands
  - Real-time transaction notifications

## Commands

- `/register` - Create a new Sycash account
- `/verify <code>` - Verify your account with the provided code
- `/balance` - Check your current balance
- `/pay <user> <amount>` - Send money to another Sycash user
- `/withdraw` - Withdraw funds from your account
- `/add_money` - Add funds to your account
- `/settings` - View and update your account settings

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/sycash.git
cd sycash
```

2. Install required dependencies:
```bash
pip install -r requirements.txt
```

3. Configure your environment variables:
- Create a `.env` file with the following variables:
```env
DISCORD_API_KEY=your_discord_bot_token
STRIPE_API_KEY=your_stripe_key
PAYPAL_CLIENT_ID=your_paypal_client_id
PAYPAL_CLIENT_SECRET=your_paypal_client_secret
COINBASE_API_KEY=your_coinbase_api_key
ENCRYPTION_KEY=your_encryption_key
SMTP_HOST=your_smtp_host
SMTP_USER=your_smtp_user
SMTP_PASSWORD=your_smtp_password
```

4. Set up the database:
```bash
python db_manage.py
```

5. Start the bot:
```bash
python bot.py
```

## Dependencies

- `interactions.py` - Discord bot framework
- `flask` - Web server for payment webhooks
- `stripe` - Payment processing
- `paypalrestsdk` - PayPal integration
- `coinbase-commerce` - Cryptocurrency payments
- `cryptography` - Data encryption
- `pillow` - Image processing

## Architecture

The project consists of several key components:

- `bot.py` - Main Discord bot implementation
- `db_manage.py` - Database management and user data handling
- `webhook.py` - Payment webhook handlers
- `sypay.py` - Payment gateway integrations
- `stars.py` - Rating system implementation

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## Security

This project handles financial transactions and sensitive user data. Always ensure:

- All API keys are kept secure and not committed to version control
- Use environment variables for sensitive configuration
- Regularly update dependencies to patch security vulnerabilities
- Follow security best practices when deploying

## Contact

lagshiift@gmail.com

## Acknowledgments

- Discord.py community
- Stripe documentation
- PayPal developers documentation
- Coinbase Commerce API documentation
