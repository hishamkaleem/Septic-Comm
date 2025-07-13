<a id="readme-top"></a>

Follow this guide in the given order of steps to setup the AWS data pipeline


## Notehub Setup
1. Begin by creating a new account and project at [Notehub](https://blues.com/notehub/)
2. Visit [Notehub.io](https://notehub.io/projects) and take note of your project's `ProductUID`
3. Replace the `prodID` macro at the top of the `NoteSketch.ino` file with this `ProductUID` string
4. Compile and run the `NoteSketch.ino` code to register the notecard device to the project

## AWS Setup
### S3 Bucket
Create an AWS account and a general-purpose AWS S3 bucket for data storage at [AWS S3](https://aws.amazon.com/s3/). 

### Lambda Function
1. Visit [AWS Lambda](https://aws.amazon.com/lambda/) and create a function from scratch. Select the runtime to be `Python 3.12`
2. In the function's `Layers` menu, add a new layer and choose the `Specify an ARN` option. Copy and paste the HTTP Requests ARN below into the field and press `Verify`
```sh
   arn:aws:lambda:ca-central-1:770693421928:layer:Klayers-p312-requests:15
```
3. Copy/paste the code in the `lambda.py` file into the function's `Code Source` menu and change the `bucket_name` variable to your S3 bucket's name
4. In your [Notehub](https://notehub.io/projects) project, navigate to the `Devices` tab and take note of your `Device UID`. Replace the `device_uid` variable in the lambda function code
  with your `Device UID`
4. Go to your project settings tab and take note of your `Project UID`. Replace the `project_uid` variable in the function code with your `Project UID`
5. In project settings, scroll down to the `Programmatic API access` menu. Click `Generate Programmatic Access` and replace the `clientID` variable 
  in the function code with the given client ID and the `clientSecret` variable with the given client secret before clicking save
6. Click `Deploy` in the lambda `Code Source` menu to push and sync the code changes

### API Gateway 
1. Visit [AWS API Gateway](https://aws.amazon.com/api-gateway/) and create an API via the `HTTP API` option
2. Once created, click on the `Routes` tab and create a route with the `POST` option
3. Go to the `Integrations` tab and create an integration. Select the previously created route and choose the `Integration Type` as `Lambda Function`. Then select your previously
created lambda function from the options listed
4. Click create and take note of the `Default Endpoint` in the `API: XYZ...` tab to be used for the Notehub route

## Notehub to AWS Route
1. In your [Notehub](https://notehub.io/projects) project, go to the `Routes` tab and create a route by selecting the `General HTTP/HTTPS Request/Response` option
2. In the `URL` bar, paste your API Gateway `Default Endpoint` and in the `Filters` menu choose `Selected Notefiles` and only select `tankdata.qo`. Also choose `Body Only`
in the `Data` tab and then create the route


Data pipelining has now been set up and the sensor readings should appear in both Notehub (under `Events`) and your S3 Bucket as JSON files