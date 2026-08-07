# KhulnaSoft Engineering Knowledge OS SDK (generated). Do not hand-edit.

module KhulnaSoft
  BASE = 'https://khulnasoft.github.io/api'.freeze

  module_function

  def resources
    BASE + '/resources'
  end

  def resource(slug)
    BASE + '/resources/{slug}'.gsub('{slug}', slug)
  end

  def twin(slug)
    BASE + '/resources/{slug}/twin'.gsub('{slug}', slug)
  end

  def context(slug)
    BASE + '/resources/{slug}/context'.gsub('{slug}', slug)
  end

  def recommendations(slug)
    BASE + '/resources/{slug}/recommendations'.gsub('{slug}', slug)
  end

  def graph
    BASE + '/graph'
  end

  def impact
    BASE + '/impact'
  end

  def events
    BASE + '/events'
  end

  def analytics
    BASE + '/analytics'
  end

  def release
    BASE + '/release'
  end

end
