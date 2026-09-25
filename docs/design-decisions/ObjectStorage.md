# Object Storage 17th Sep 2026
I explored different third-party candidates for object storage including Garage RustFS and SeaweedFS.
I compared the three packages in what they offer, their restrictions and licensing.
RustFS was ultimately chosen as the de facto object storage solution due to it meeting all of my requirements.

## The Goal
Future plans for the application will require some form of file storage and organisation.
There are two paths that I can take to introducing this feature; building a custom solution for the problem or use third-party packages.
Custom building would cost me time and would also be less reliable than a third-party solution.
I would also have to ensure that my solution would work consistently and be deterministic; consistency being the bigger concern.

Therefore I chose to use a third-party package that would offer a Docker solution.
This would then provide me an easy way to swap and replace different solutions easily.
I settled with the Amazon S3 API and had the following three solutions: -

1. Garage
2. RustFS
3. SeaweedFS

## Candidates
### Garage
Garage was released Nov 17th 2021 with no commercial restrictions on use.
It can be deployed on multiple low spec machines and linked up for redundant storage.
It also uses the AGPLv3 license for its source code and usage.
However it requires you to install its CLI to then generate a key and secret to be used.

### RustFS
RustFS was released Nov 23rd 2023 making it the newest out of the three.
It uses the Apache 2.0 license and comes with no commercial restrictions to use.
It is an alternative to MinIO (being built in rust) and advertised as a high-performance storage.
However it is the least mature application with its first stable release on the 16th September 2026.

### SeaweedFS
SeaweedFS was released Jul 14th 2014 making it the most mature package out of the three.
It can handle billions of files with data redundancy included.
It can also be used as a filesystem as well as an object storage.
It uses the Apache 2.0 license however requires a subscription in order to use for production environments.

## Decision
After researching the three I went with RustFS.
My main reason was it had met all of my requirements which were: -

1. Docker container version
2. Amazon S3 API compatibility
3. Easy setup configuration
4. Specify storage location

Although it has just released its first stable version, it has similar support and recognition to SeaweedFS in terms of GitHub stars.
This gives me confidence that the package would be greatly supported in the future with new releases and bug fixes.

SeaweedFS was not selected due to its licensing restrictions.
Garage was also no option as it had a more restrictive setup, requiring the garage CLI to create valid keys and secrets (unlike RustFS).
This to me added more friction as I just wanted a plug-and-play solution.

RustFS was therefore the best fit for my requirements.
