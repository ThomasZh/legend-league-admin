# CentOS7安装mysql数据库

### 在Centos7中用MariaDB代替了mysql数据库。
  '' # yum install mariadb
	'' # yum install mysql-devel
	'' # yum install MySQL-python

### mariadb数据库的启动命令是：
  '' # systemctl start mariadb  #启动MariaDB
  '' # systemctl stop mariadb  #停止MariaDB
  '' # systemctl restart mariadb  #重启MariaDB
  '' # systemctl enable mariadb  #设置开机启动
  '' # mysql_secure_installation ==> 设置 root密码等相关

### 创建mysql用户
  '' $ mysql -u root -p @>密码 
  //创建用户
  '' MariaDB> insert into mysql.user(Host,User,Password) values(‘localhost’,’legend’, password(‘20170123’)); 
  //刷新系统权限表
  '' MariaDB>flush privileges; 
  这样就创建了一个名为：legend  密码为：20170123  的用户。
  //退出后登录一下
  ''  MariaDB>exit;
  '' $ mysql -u legend -p @>输入密码
  ''  MariaDB>登录成功

### 为用户授权
  //登录MYSQL（有ROOT权限）。我里我以ROOT身份登录. 
  '' $ mysql -u root -p @>密码 
  //首先为用户创建一个数据库(legend)
  ''  MariaDB>create database legend; 
  //授权legend用户拥有legend数据库的所有权限
   '' MariaDB>grant all privileges on legend.* to legend@localhost IDENTIFIED BY '20170123'; 
  //刷新系统权限表 
  '' MariaDB>flush privileges; 

### 创建表: 联盟

  '' $ mysql -u legend -p @>输入密码
  ''  MariaDB>use legend;
  '' MariaDB>show tables;

CREATE TABLE 'league' (
  '_id' char(32) NOT NULL,
  '_name' varchar(255) DEFAULT NULL,
  'create_time' bigint(19) NOT NULL DEFAULT '0',
  '_status' int(8) NOT NULL DEFAULT '0',
  PRIMARY KEY ('_id')
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

INSERT INTO league (_id, _name) VALUES ('f24794c7e1d511e68c0aa45e60efbf2d', 'legend-league');


### 创建表: 联盟管理员

  '' $ mysql -u legend -p @>输入密码
  ''  MariaDB>use legend;
  '' MariaDB>show tables;

CREATE TABLE league_admin (
  league_id char(32) NOT NULL DEFAULT '0000000000000000000000000000000',
  account_id char(32) NOT NULL DEFAULT '0000000000000000000000000000000',
  create_time bigint(19) NOT NULL DEFAULT 0,
  _status int(8) NOT NULL DEFAULT 0,
  _rank int(8) NOT NULL DEFAULT 0,
  PRIMARY KEY (account_id, league_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

INSERT INTO league_admin (league_id, account_id) VALUES ('f24794c7e1d511e68c0aa45e60efbf2d', '128be5bee0a411e69c5200163e023e51');
