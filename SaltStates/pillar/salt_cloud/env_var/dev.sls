nginx:
  ami: ami-123456789
  keyName: LaoMao-{{ salt['grains.get']('env') }}
  privateKeyLocation: /srv/secrets/LaoMao-dev.pem
  iamProfile: LaoMao-ec2-instanceprofile-role
  hostName: HostName
  subnetId: subnet-123456789