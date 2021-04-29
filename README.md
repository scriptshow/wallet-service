# wallet-service

**NOTE: The documentation of this project was done originally in spanish, the text has been translated to english.**

## Description

You want to develop a wallet service with a Rest API that allows you to make payments
exclusively using a token.

Different types of endpoint users are considered to perform the following operations:

- Client: must be able to register for the service, create one or more accounts
wallet (which will be identified by a unique token), recharge the balance of your accounts, consult
the status of your accounts and list the operations of your accounts.

- Commerce: must be able to register for the service, create a wallet account,
make charges to a customer's wallet account with reference to the token of the
account and list the operations of your trading account.

The history of operations should include both successful recharge operations
and collection, such as failed collection attempts due to lack of balance.

The fields necessary for the registration of customers and businesses, as well as the process of
Generation of the token associated with each of the accounts is up to the candidate's choice. Not
It is necessary to take care of the customer's payment process during the recharge operation of the
balance of your accounts.

## Objectives to complete


1. Indicates how the performance of the trade listing service can be optimized.

    - Answer: According to the application requirements, they do not specify that there could be
      some kind of filter when listing the operations of the accounts, I even enter
      in doubt if customers want all the operations of their accounts in a single
      query, instead of by wallet account (as I have implemented it). But definitely,
      one of the best ways to improve the performance of this query is to filter
      by date range, also I already put an index to the column where the date of
      each transaction for future use. Additionally, like this table, as a history of operations,
      its growth is expected to be very high, to improve performance it could be done
      partitions of it using the "date" field (which saves the datetime of each operation),
      creating for example, a partition for each trading day. When using the database of
      postgresql, it is very easy to introduce a function to create the partitions for you automatically.

2. What alternatives do you propose in the event that the application's relational database is
become a bottleneck due to saturation in read operations? And for those of
writing?
   
    - Answer: When the bottleneck is generated in the reading operations part, we must
      to start looking if our solution could be to go through a data caching system, such as
      it could be Redis. But this system requires that the data to be consulted does not change with
      very high frequency, otherwise we would be showing outdated information, or even replicating
      the problem with a more complex system to maintain. On the other hand we could also add
      read-only replicas to our database, and pass all read operations
      distributed among the different replicas.
      For the bottleneck part in write operations, some databases like
      MySQL or PostgreSQL (the one we have chosen for this project!) Have options to perform
      writes in blocks, instead of row by row, this would be useful if the trades of our application
      they will need to make the same charge to multiple clients (as if they were charging a subscription,
      for example). Another option to solve writing problems is to make different partitions
      for the history table (in our case the one with the most overhead) and distribute them each
      one of them in different filesystem, using independent physical disks, thus distributing the
      Workload.
      Finally we can also choose a solution that helps to scale the bases horizontally
      relational data, in our case, using PostgreSQL, it would be Citus (www.citusdata.com/)

3. They say that relational databases do not scale well, it occurs to me to mount the project
with some NoSQL, what do you recommend?
   
    - Answer: For applications that handle money or information transactions especially
      sensitive that it needs to be very consistent, it is always sought that they meet the standards
      ACID (atomicity, consistency, isolation, durability) where relational databases
      they are the best candidate. However, there are also some NoSQL databases that comply with these
      standards, such as: CouchDB or FoundationDB. Currently there are also many
      utilities to scale SQL databases like Citus, so personally
      for this application, I would recommend using some SQL database.

4. What kind of metrics and services can help us verify that the API and the server
they work right?
   
    - Answer: As part of the monitoring, since our application is based on dockers,
      the first service to monitor would be the docker service, followed by the docker instances
      created for this application (the image from the web, and the image from the database), that are
      up and without infinitely resetting.
      Additionally, an extra monitoring can be added to some endpoints of the Rest API,
      You could even create a single '/ status' endpoint, which would only return the code 200,
      thus meaning the correct functioning of the REST service. Another extra check that can be
      add, is to log in with a user account for this type of automation. In the
      part of the server, you can add metrics to see the consumption of memory, cpu and I / O of
      the filesystem, as well as the free disk space.

## Bonus

1. We would like to contemplate that the recharge and collection operations are at all times
atomic, that is, if you try to charge two operations at the same time, they should only be
accepted if there is enough money in the account to complete both.

It should be avoided that due to some error in the integration of the trade, operations of
payment.

2. Deploy the project in the instance provided. Ideally with Docker, you can include it
all in the single repository. You can choose to do a manual or automated deployment.
In the second case, we also ask you to provide us with the code that you have
employee.

# Documentation

Here begins the documentation of the finished application, the following must be taken into account
decisions that have been made in the project:
- Both customers and businesses will use the same endpoint "/ wallet" when interacting with their wallets,
since the wallets are identical objects for both.
- Merchants can only create one portfolio, while customers have the portfolio limit
set to a variable, which by default are unlimited.
- Both customers and businesses can make deposits in their portfolios.
- Since merchants can also make deposits to their own portfolios, it is contemplated that a merchant
You can charge the portfolio of another merchant, since they can interact with each other.
- Only merchants will be able to charge other portfolios.

## Installation

The application is based on docker-compose, which brings the application and the database to be used embedded,
so all you need is to have docker and docker-compose installed.

## Configuration
Inside docker-compose.yml you will find the following parameters, which you can modify:

WALLET_SERVICE_LOG_LEVEL -> Values allowed: ['debug', 'info', 'warning', 'error', 'critical']

WALLET_SERVICE_SECRET_KEY -> Secret key used by Django project

WALLET_SERVICE_DEBUG_MODE -> Values allowed: ['True', 'False']

WALLET_SERVICE_ALLOWED_HOSTS -> Default: "localhost 127.0.0.1"

WALLET_SERVICE_ALLOWED_ORIGINS -> Default: "http: // localhost: 8000 http://127.0.0.1:8000"

WALLET_SERVICE_AUTH_TOKEN_EXPIRATION -> Expiration time for our authentication token (in hours)

WALLET_SERVICE_MAX_WALLETS_BY_CLIENT -> Limit of portfolios created by each client, 0 for unlimited

## Running the application

Go to where our docker-compose.yml is located within the project.

Run the following command to build our docker-compose:

`docker-compose build`

Run the following command to launch our docker-compose:

`docker-compose up`

## Automatic deployment

To automatically deploy our application with the default values, we are going to use ansible,
so the only thing we are going to need is a machine with ansible installed, take our file with us
'ansible_deployment.yml' and run the following command:

`ansible-playbook ansible_deployment.yml -i HOSTNAME, -e" githubuser = GITHUB_USER "-e" githubpassword = GITHUB_PASS "--private-key" PRIVATE_KEY_PATH "-u USERNAME`

- HOSTNAME: It must be replaced by the IP of the server where to install our application
- USERNAME: It must be replaced by the user of the server where our application is going to be deployed
- PRIVATE_KEY_PATH: It must be replaced by the path where the private_key is found to authenticate us
- GITHUB_USER: Must be replaced by the GitHub user with permissions on the repository
- GITHUB_PASS: It must be replaced by the GitHub password with premises in the repository

## API Documentation

### Endpoints for clients

***Sign up***

Method: POST

URL: _/client/signup_

Body: `{
    "email": "string",
    "password": "string",
    "client": {
        "first_name": "string",
        "last_name": "string",
        "phone_number": "+34666666666"
    }
}`

Response: `{"token": "auth_token"}`


***Log in***

Method: POST

URL: _/client/login_

Body: `{
    "email": "string",
    "password": "string"
}`

Response: `{"token": "auth_token"}`


***Log out***

Method: POST

URL: _/client/logout_

Headers: `{
    "Authorization": "Token auth_token"
}`

Body: `{}`

Response: ``


### Endpoints for companies

***Sign up***

Method: POST

URL: _/company/signup_

Body: `{
    "email": "string",
    "password": "string",
    "company": {
        "name": "string",
        "url": "string",
        "first_name": "string",
        "last_name": "string",
        "phone_number": "+34666666666"
    }
}`

Response: `{"token": "auth_token"}`


***Log in***

Method: POST

URL: _/company/login_

Body: `{
    "email": "string",
    "password": "string"
}`

Response: `{"token": "auth_token"}`


***Log out***

Method: POST

URL: _/company/logout_

Headers: `{
    "Authorization": "Token auth_token"
}`

Body: `{}`

Response: ``


### Endpoints managing wallets


***Create new wallets***

Method: POST

URL: _/wallet/create_

Headers: `{
    "Authorization": "Token auth_token"
}`

Body: `{}`

Response: 
`{
    "wallet": "your_wallet_token"
}`


***Make a deposit***

Method: POST

URL: _/wallet/deposit_

Headers: `{
    "Authorization": "Token auth_token"
}`

Body: `{
    "wallet": "your_wallet_token",
    "amount": "amount_to_deposit"
}`

Response: 
`{
    "wallet": "your_wallet_token",
    "balance": total_balance_after_deposit
}`


***Get information from a wallet***

Method: GET

URL: _/wallet/info/< your_wallet_token >_

Headers: `{
    "Authorization": "Token auth_token"
}`

Response: 
`{
    "wallet": "your_wallet_token",
    "balance": current_balance
}`


***Get information for all your wallets***

Method: GET

URL: _/wallet/list_

Headers: `{
    "Authorization": "Token auth_token"
}`

Response: 
`[
    {
        "wallet": "your_wallet_token",
        "balance": current_balance
    }, ...
]`


***Make a charge to a client (only available for companies)***

Method: POST

URL: _/wallet/charge_

Headers: `{
    "Authorization": "Token auth_token"
}`

Body: `{
    "wallet": "wallet_to_make_a_charge",
    "amount": amount_to_be_charged,
    "summary": "short description about the charge"
}`

Response: 
`{
    "wallet": "your_wallet_token",
    "balance": current_balance_after_receive_the_charge
}`


***Get the operation history for a wallet***

Method: GET

URL: _/wallet/history/< your_wallet_token >_

Headers: `{
    "Authorization": "Token auth_token"
}`

Response: 
`[
    {
        "summary": "short description about the operation",
        "source__token": "wallet_from_money_was_charged" or empty if its a deposit,
        "target__token": "your_wallet_where_the_money_was_deposit",
        "amount": the_amount_transfered_or_deposit,
        "success": true,
        "date": "2021-04-11T11:05:13.591091Z"
    }, ...
]`
