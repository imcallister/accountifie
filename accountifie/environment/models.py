from django.db import models

class Variable(models.Model):
  key = models.CharField(max_length=100, unique=True)
  value = models.CharField(max_length=100)

  def __unicode__(self):
    return self.key


class Config(models.Model):
  name = models.CharField(max_length=20, unique=True)
  reporting = models.ForeignKey(Variable, on_delete=models.CASCADE)

class Alias(models.Model):
  name = models.CharField(max_length=100)
  display_as = models.CharField(max_length=100)
  context = models.ForeignKey('gl.Company', null=True, blank=True, on_delete=models.CASCADE)

def get_env_variable(key):
  try:
    return Variable.objects.get(key=key).value
  except:
    raise ValueError("Can't find system variable %s" %key)

def get_env_alias(name):
  try:
    return Alias.objects.get(name=name).to_dict()
  except:
    raise ValueError("Can't find alias variable %s" %key)

def get_env_config(key):
  try:
    return Config.objects.get(name=name).reporting.value
  except:
    raise ValueError("Can't find config variable %s" %key)