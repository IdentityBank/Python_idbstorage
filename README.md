# Python project - Identity Bank storage system

[Identity Bank](https://www.identitybank.eu)

### idbstorage
The file storage engine for Identity Bank. This controller provides functionality to allow storing and retrieval of stored data. The first phase implements direct secure storage in S3 buckets. For future improvements we are planning to implement encryption and decryption on the fly where keys are separated and provided by customers or stored at our KMS system.
